import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.report import ReportCreateRequest
from app.services.analyzer import build_player_list, calculate_player_metrics
from app.services.coach import generate_report
from app.services.opendota import fetch_match
from app.services.storage import database_backend, get_report, init_db, list_reports, save_report

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
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/matches/{match_id}/players")
async def get_match_players(match_id: int) -> dict:
    match = await get_match(match_id)
    return {"match_id": match_id, "players": build_player_list(match)}


@app.post("/reports")
async def create_report(request: ReportCreateRequest) -> dict:
    match = await get_match(request.match_id)
    metrics = calculate_player_metrics(match, request.player_slot, request.role)
    report = generate_report(match, metrics)
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
