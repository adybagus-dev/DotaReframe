from __future__ import annotations

import os
from urllib.parse import urlencode, urlparse
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.schemas.report import ReportCreateRequest
from app.services.analyzer import build_player_list, calculate_player_metrics, hero_name, player_result
from app.services.coach import generate_report
from app.services.opendota import OpenDotaError, fetch_match, fetch_recent_matches
from app.services.storage import (
    database_backend,
    get_report,
    init_db,
    list_report_payloads,
    list_reports,
    save_report,
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


@app.post("/reports")
async def create_report(request: ReportCreateRequest) -> dict:
    match = await get_match(request.match_id)
    metrics = calculate_player_metrics(match, request.player_slot, request.role)
    if request.account_id and not metrics.get("account_id"):
        metrics["account_id"] = request.account_id
    report = generate_report(match, metrics, list_report_payloads())
    save_warning = None

    try:
        save_report(report)
    except Exception as exc:  # pragma: no cover - storage should not hide report
        save_warning = str(exc)

    payload = report.model_dump()
    if save_warning:
        payload["save_warning"] = save_warning
    return payload


@app.get("/reports")
def get_reports() -> list[dict]:
    return list_reports()


@app.get("/reports/{report_id}")
def get_saved_report(report_id: str) -> dict:
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


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


@app.get("/auth/steam/login")
def steam_login(return_to: Optional[str] = None) -> RedirectResponse:
    frontend_return = _safe_frontend_return(return_to)
    backend_public_url = os.getenv("BACKEND_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")
    callback = f"{backend_public_url}/auth/steam/callback"
    query = urlencode(
        {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": f"{callback}?return_to={frontend_return}",
            "openid.realm": callback.rsplit("/auth/steam/callback", 1)[0],
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
    )
    return RedirectResponse(f"https://steamcommunity.com/openid/login?{query}")


@app.get("/auth/steam/callback")
async def steam_callback(request: Request, return_to: Optional[str] = None) -> RedirectResponse:
    frontend_return = _safe_frontend_return(return_to)
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
    separator = "&" if "?" in frontend_return else "?"
    return RedirectResponse(f"{frontend_return}{separator}steam_account_id={account_id}")
