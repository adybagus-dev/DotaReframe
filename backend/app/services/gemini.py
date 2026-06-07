from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

import httpx

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiError(Exception):
    pass


def _clean_json_payload(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def is_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def refine_report_language(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    url = f"{GEMINI_API_URL}/models/{model}:generateContent?key={api_key}"
    prompt = {
        "role": payload.get("role"),
        "hero": payload.get("hero"),
        "result": payload.get("result"),
        "summary": payload.get("summary"),
        "main_problem": payload.get("main_problem"),
        "match_story": payload.get("match_story"),
        "next_match_mission": payload.get("next_match_mission"),
        "progress": payload.get("progress"),
        "practice_drills": payload.get("practice_drills", []),
        "training_plan": payload.get("training_plan", []),
        "summary_note": payload.get("summary_note"),
        "reflection_prompt": payload.get("reflection_prompt"),
    }
    instruction = (
        "You rewrite Dota coaching text in simple, day-to-day language.\n"
        "Keep all facts, numbers, and role labels exactly grounded in the input.\n"
        "Do not invent new evidence, timings, or statistics.\n"
        "Return JSON only with these keys:\n"
        "match_story, main_problem, practice_drills, training_plan, next_match_mission, progress, "
        "summary_note, reflection_prompt\n"
        "Where practice_drills and training_plan stay arrays with the same length and intent.\n"
        "summary_note must be one short saved-report card sentence.\n"
        "reflection_prompt must be one direct question the player can answer after reading the report.\n"
        "Make the wording clear, short, and easy to read."
    )

    try:
        with httpx.Client(timeout=12) as client:
            response = client.post(
                url,
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": instruction},
                                {"text": json.dumps(prompt, ensure_ascii=False)},
                            ],
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1200,
                    },
                },
            )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
        if not text:
            return None
        parsed = json.loads(_clean_json_payload(text))
        if not isinstance(parsed, dict):
            return None
        return parsed
    except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise GeminiError(str(exc)) from exc


def generate_dashboard_note(payload: dict[str, Any]) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    url = f"{GEMINI_API_URL}/models/{model}:generateContent?key={api_key}"
    prompt = {
        "total_reports": payload.get("total_reports"),
        "mission_streak": payload.get("mission_streak"),
        "active_mission": payload.get("active_mission"),
        "latest_progress": payload.get("latest_progress"),
        "latest_report": payload.get("latest_report"),
    }
    instruction = (
        "Write one short dashboard coach note for DotaReframe.\n"
        "Use simple day-to-day language.\n"
        "Do not invent facts or stats.\n"
        "Keep it to one sentence, under 24 words if possible.\n"
        "Focus on what the player should do next or what improved.\n"
        "Return JSON only with a single key: note."
    )

    try:
        with httpx.Client(timeout=12) as client:
            response = client.post(
                url,
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": instruction},
                                {"text": json.dumps(prompt, ensure_ascii=False)},
                            ],
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 120,
                    },
                },
            )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )
        if not text:
            return None
        parsed = json.loads(_clean_json_payload(text))
        if not isinstance(parsed, dict):
            return None
        note = parsed.get("note")
        if isinstance(note, str):
            cleaned = note.strip()
            return cleaned or None
        return None
    except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise GeminiError(str(exc)) from exc
