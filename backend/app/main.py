from __future__ import annotations

import os
from urllib.parse import urlencode, urlparse
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.schemas.report import ReportCreateRequest, ReportFeedbackRequest
from app.services.analyzer import build_player_list, calculate_player_metrics, hero_name, player_result
from app.services.coach import generate_report
from app.services.gemini import GeminiError, generate_dashboard_note
from app.services.opendota import OpenDotaError, fetch_match, fetch_recent_matches
from app.services.storage import (
    database_backend,
    find_duplicate_report,
    get_benchmark_samples,
    get_feedback,
    get_report,
    init_db,
    list_report_payloads,
    list_reports,
    save_report,
    save_feedback,
)
from app.services.identity import (
    attach_steam,
    consume_exchange,
    consume_steam_state,
    create_exchange,
    create_session,
    create_steam_state,
    init_identity_db,
    resolve_session,
    revoke_session,
)

app = FastAPI(title="DotaReframe API", version="0.1.0")

default_origins = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
allowed_origins = [origin.strip() for origin in os.getenv("FRONTEND_ORIGINS", default_origins).split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()
    init_identity_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": database_backend()}


@app.get("/matches/{match_id}")
async def get_match(match_id: int) -> dict:
    try:
        return await fetch_match(match_id)
    except OpenDotaError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.get("/matches/{match_id}/players")
async def get_match_players(match_id: int) -> dict:
    match = await get_match(match_id)
    return {"match_id": match_id, "players": build_player_list(match)}


def current_profile(x_session_token: Optional[str] = Header(default=None)) -> dict:
    profile = resolve_session(x_session_token)
    if profile is None:
        raise HTTPException(status_code=401, detail="Your session expired. Refresh and try again.")
    return profile


@app.post("/sessions")
def ensure_session(x_session_token: Optional[str] = Header(default=None)) -> dict:
    profile = resolve_session(x_session_token)
    if profile:
        return {"token": x_session_token, "profile": profile}
    token, profile = create_session()
    return {"token": token, "profile": profile}


@app.post("/sessions/logout")
def logout_session(
    x_session_token: Optional[str] = Header(default=None),
) -> dict:
    revoke_session(x_session_token)
    token, profile = create_session()
    return {"token": token, "profile": profile}


async def _create_personal_report(request: ReportCreateRequest, profile: dict) -> dict:
    if request.role:
        duplicate = find_duplicate_report(profile["id"], request.match_id, request.player_slot, request.role)
        if duplicate:
            duplicate.setdefault("feedback", None)
            return duplicate

    match = await get_match(request.match_id)
    metrics = calculate_player_metrics(match, request.player_slot, request.role)
    verified_account = profile.get("steam_account_id")
    if verified_account and metrics.get("account_id") != verified_account:
        raise HTTPException(status_code=403, detail="That player is not connected to your Steam profile.")
    duplicate = find_duplicate_report(profile["id"], request.match_id, request.player_slot, metrics["role"])
    if duplicate:
        duplicate.setdefault("feedback", None)
        return duplicate
    report = generate_report(
        match,
        metrics,
        list_report_payloads(profile_id=profile["id"]),
        get_benchmark_samples(),
    )
    report.id = f"{report.id}-{profile['id'][:8]}"
    save_warning = None

    try:
        save_report(report, profile["id"], metrics)
    except Exception as exc:  # pragma: no cover - storage should not hide report
        save_warning = str(exc)

    payload = report.model_dump()
    if save_warning:
        payload["save_warning"] = save_warning
    return payload


@app.post("/me/reports")
async def create_personal_report(request: ReportCreateRequest, profile: dict = Depends(current_profile)) -> dict:
    return await _create_personal_report(request, profile)


@app.get("/me/reports")
def get_personal_reports(profile: dict = Depends(current_profile)) -> list[dict]:
    return list_reports(profile["id"])


@app.get("/me/reports/{report_id}")
def get_personal_report(report_id: str, profile: dict = Depends(current_profile)) -> dict:
    report = get_report(report_id, profile["id"])
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    report["feedback"] = get_feedback(profile["id"], report_id)
    return report


@app.put("/me/reports/{report_id}/feedback")
def update_report_feedback(
    report_id: str,
    request: ReportFeedbackRequest,
    profile: dict = Depends(current_profile),
) -> dict:
    try:
        return save_feedback(profile["id"], report_id, request.helpful, request.reason)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc


def _mission_streak(reports: list[dict]) -> int:
    streak = 0
    for report in reports:
        progress = report.get("progress")
        if not progress:
            continue
        if not progress.get("completed"):
            break
        streak += 1
    return streak


def _dashboard_coach_note(profile: dict, reports: list[dict], latest: dict | None, latest_progress: dict | None) -> str:
    payload = {
        "total_reports": len(reports),
        "mission_streak": _mission_streak(reports),
        "active_mission": latest.get("next_match_mission") if latest else None,
        "latest_progress": latest_progress,
        "latest_report": latest,
    }

    try:
        note = generate_dashboard_note(payload)
    except GeminiError:
        note = None
    except Exception:
        note = None

    if note:
        return note

    if latest_progress and latest_progress.get("completed"):
        return "You completed your last mission. Open the next review and keep the streak moving."
    if latest_progress:
        return "Your last mission is still in progress. One more review will show whether the habit is changing."
    if latest:
        return f"Your latest report is on {latest['hero']}. Open it when you want the next clear fix."
    return "Start with one review, then come back after your next match to see what improved."


@app.get("/me/dashboard")
def get_dashboard(profile: dict = Depends(current_profile)) -> dict:
    reports = list_report_payloads(profile_id=profile["id"])
    latest = reports[0] if reports else None
    latest_progress = latest.get("progress") if latest else None
    return {
        "profile": profile,
        "total_reports": len(reports),
        "mission_streak": _mission_streak(reports),
        "active_mission": latest.get("next_match_mission") if latest else None,
        "latest_progress": latest_progress,
        "coach_note": _dashboard_coach_note(profile, reports, latest, latest_progress),
        "recent_reports": list_reports(profile["id"])[:4],
    }


@app.get("/players/{account_id}/recent-matches")
async def get_recent_matches(account_id: int) -> dict:
    try:
        matches = await fetch_recent_matches(account_id)
    except OpenDotaError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    items = []
    for match in matches[:10]:
        slot = int(match.get("player_slot") or 0)
        items.append(
            {
                "match_id": int(match.get("match_id") or 0),
                "player_slot": slot,
                "hero": hero_name(match.get("hero_id")),
                "result": player_result(match, slot),
                "kda": f"{match.get('kills', 0)} / {match.get('deaths', 0)} / {match.get('assists', 0)}",
                "duration_minutes": round(int(match.get("duration") or 0) / 60),
                "started_at": int(match.get("start_time") or 0),
            }
        )
    return {"account_id": account_id, "matches": items}


@app.get("/me/recent-matches")
async def get_my_recent_matches(profile: dict = Depends(current_profile)) -> dict:
    account_id = profile.get("steam_account_id")
    if not account_id:
        return {"account_id": None, "matches": []}
    return await get_recent_matches(int(account_id))


@app.get("/me/matches/{match_id}/review-context")
async def get_review_context(match_id: int, profile: dict = Depends(current_profile)) -> dict:
    account_id = profile.get("steam_account_id")
    if not account_id:
        raise HTTPException(status_code=400, detail="Connect Steam to use the fast review flow.")
    match = await get_match(match_id)
    player = next(
        (item for item in match.get("players", []) if int(item.get("account_id") or 0) == int(account_id)),
        None,
    )
    if player is None:
        raise HTTPException(status_code=404, detail="Your Steam player was not found in this match.")
    metrics = calculate_player_metrics(match, int(player["player_slot"]))
    summary = next(item for item in build_player_list(match) if item["player_slot"] == int(player["player_slot"]))
    return {"player": summary, "detected_role": metrics["role"], "match_id": match_id}


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", allowed_origins[0]).rstrip("/")


def _safe_frontend_return(value: Optional[str]) -> str:
    fallback = f"{_frontend_url()}/match"
    if not value:
        return fallback
    parsed = urlparse(value)
    allowed = {urlparse(origin).netloc for origin in allowed_origins}
    if parsed.scheme not in {"http", "https"} or parsed.netloc not in allowed:
        return fallback
    return value


@app.post("/auth/steam/start")
def steam_login(
    payload: dict,
    profile: dict = Depends(current_profile),
) -> dict:
    return_to = payload.get("return_to")
    frontend_return = _safe_frontend_return(return_to)
    backend_public_url = os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    state = create_steam_state(profile["id"], frontend_return)
    callback = f"{backend_public_url}/auth/steam/callback?state={state}"
    query = urlencode(
        {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": callback,
            "openid.realm": backend_public_url,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
    )
    return {"auth_url": f"https://steamcommunity.com/openid/login?{query}"}


@app.get("/auth/steam/callback")
async def steam_callback(request: Request, state: str) -> RedirectResponse:
    state_data = consume_steam_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Steam sign-in expired. Please try again.")
    frontend_return = _safe_frontend_return(state_data["return_to"])
    params = {key: value for key, value in request.query_params.items() if key.startswith("openid.")}
    params["openid.mode"] = "check_authentication"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            verification = await client.post("https://steamcommunity.com/openid/login", data=params)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Steam sign-in could not be verified.") from exc

    claimed_id = request.query_params.get("openid.claimed_id", "")
    valid_claim = claimed_id.startswith(
        ("http://steamcommunity.com/openid/id/", "https://steamcommunity.com/openid/id/")
    )
    if "is_valid:true" not in verification.text or not valid_claim:
        raise HTTPException(status_code=401, detail="Steam sign-in was not valid.")

    steam_id = int(claimed_id.rsplit("/", 1)[-1])
    account_id = steam_id - 76561197960265728
    profile_id = attach_steam(state_data["profile_id"], account_id)
    code = create_exchange(profile_id)
    callback_url = f"{urlparse(frontend_return).scheme}://{urlparse(frontend_return).netloc}/api/steam/callback"
    return RedirectResponse(f"{callback_url}?code={code}")


@app.post("/auth/steam/exchange")
def steam_exchange(payload: dict) -> dict:
    token = consume_exchange(str(payload.get("code") or ""))
    if not token:
        raise HTTPException(status_code=400, detail="Steam sign-in code expired.")
    profile = resolve_session(token)
    return {"token": token, "profile": profile}


# Temporary compatibility endpoints for old clients. They are private now.
@app.post("/reports")
async def create_report_compat(request: ReportCreateRequest, profile: dict = Depends(current_profile)) -> dict:
    return await _create_personal_report(request, profile)


@app.get("/reports")
def get_reports_compat(profile: dict = Depends(current_profile)) -> list[dict]:
    return list_reports(profile["id"])


@app.get("/reports/{report_id}")
def get_report_compat(report_id: str, profile: dict = Depends(current_profile)) -> dict:
    return get_personal_report(report_id, profile)
    find_duplicate_report,
    get_benchmark_samples,
    get_feedback,
