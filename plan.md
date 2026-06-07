# DotaReframe - MVP Plan

## 1. Project Summary

DotaReframe is a post-match Dota 2 improvement app. A user reviews a match, receives one evidence-based mission, and returns after the next game to see whether that habit improved.

The MVP is a local web app focused on one clear flow:

```text
Enter Match ID -> Choose Your Hero -> Read Your Review
```

The app should help the user answer:

- What happened in my match?
- What did I do wrong?
- What did I do well?
- What should I practice next game?

## 2. Target User

Primary user:

- Casual to serious Dota 2 player
- Wants to improve without reading complex analytics
- Understands basic Dota terms like farming, item timing, laning, fights, objectives, wards, and Roshan

## 3. UX Principle

The UX should be simple, readable, and written in day-by-day language.

Use phrases like:

- "You fought too early"
- "Your farming item was late"
- "You did not turn kills into towers"
- "You died in unsafe areas"
- "Focus on this next game"

Avoid phrases like:

- "Suboptimal macro-objective conversion"
- "Resource acquisition inefficiency"
- "Engagement frequency anomaly"

The app should feel like a calm coach, not a stats dashboard for analysts.

## 4. MVP Scope

The first local version should include:

1. Input match ID
2. Fetch match data from OpenDota
3. Display 10 players from the match
4. Let user choose one player
5. Calculate basic player metrics
6. Generate a structured coaching report
7. Display the report in a simple dashboard
8. Save report locally
9. Let each private guest or Steam profile view its own saved reports
10. Remember one active mission and compare it with the next reviewed match
11. Track completed-mission streaks and report usefulness feedback

MVP navigation should use a simple sidebar with only:

- New Review
- Saved Reports

The retention release should not include:

- Full rank benchmark system
- Email/password accounts; identity uses a private guest session with optional verified Steam connection
- Settings page
- Delete or edit saved report feature
- Anything outside the post-match review and saved-report flow

## 5. Match Review Report

The main output is a Match Review Report.

Report sections:

1. Match Summary
2. Main Thing To Fix
3. Performance Snapshot
4. Top 3 Mistakes
5. What You Did Well
6. Next 3 Games Training Plan
7. Match Evidence
8. AI Limitation Note

Example readable output:

```text
You played Juggernaut.

Result: Lost
Duration: 42 min
KDA: 8 / 7 / 11
Gold/min: 512
XP/min: 641

Main thing to fix:
You joined too many fights before your first major item. That slowed your farming and delayed your strong timing.

Top mistake:
You fought before your item timing.

What happened:
You joined fights before your first core item was ready.

Evidence:
- 3 deaths before minute 18
- Battle Fury finished at 17:42
- Farming slowed after minute 10

Try next game:
Farm safer until your first core item, unless your team is defending a tower.
```

## 6. Structured Report JSON

The backend should generate structured JSON before rendering the UI.

Example schema:

```json
{
  "match_id": 8123456789,
  "player_slot": 0,
  "hero": "Juggernaut",
  "role": "Safe Lane",
  "result": "Loss",
  "summary": {
    "duration_minutes": 42,
    "kda": "8/7/11",
    "gpm": 512,
    "xpm": 641,
    "last_hits": 286,
    "denies": 12,
    "hero_damage": 24100,
    "tower_damage": 1240
  },
  "main_problem": "You fought too early before your farming item.",
  "performance_snapshot": {
    "farming": "Needs Work",
    "fighting": "Good",
    "survival": "Needs Work",
    "objectives": "Low Impact"
  },
  "mistakes": [
    {
      "title": "Fought before your item timing",
      "what_happened": "You joined fights before your first core item was ready.",
      "evidence": [
        "3 deaths before minute 18",
        "Battle Fury finished at 17:42"
      ],
      "why_it_matters": "As a carry, dying before your farming item delays your strongest timing.",
      "try_next_game": "Farm safer until your first core item, unless your team is defending a tower."
    }
  ],
  "strengths": [
    "Good late-game teamfight participation"
  ],
  "training_plan": [
    "For the next 3 games, focus on reaching your first farming item before joining optional fights.",
    "After every won fight, check if your team can take a tower, Roshan, or enemy jungle."
  ],
  "confidence": "medium",
  "limitations": [
    "This review is based on match stats and may not fully understand positioning, voice calls, or team strategy."
  ]
}
```

## 7. UI Pages

### App Shell / Sidebar

Purpose:

- Provide simple dashboard navigation
- Keep the MVP focused on reviewing matches and opening saved reports

Sidebar content:

```text
DotaReframe

New Review
Saved Reports

Backend: Online
```

Behavior:

- `New Review` opens the match input flow.
- `Saved Reports` opens the local saved report list.
- Main content shows a clear page title, short supporting text, and the current screen's main action.

States:

- Backend online
- Backend unavailable
- Current route selected
- Narrow screen layout with collapsed menu

### New Review: Match Input

Route:

```text
/match
```

Purpose:

- Let user enter a Dota 2 match ID
- Start analysis

UI content:

```text
Analyze a Dota 2 Match

Paste your Dota 2 match ID
[ 8123456789 ]

[Analyze Match]

You can find match ID in your Dota 2 match history or OpenDota.
```

Useful fields:

- Match ID input
- Analyze Match button
- Helper text for where to find a match ID
- Optional shortcut to recent saved reports if reports exist

States:

- Empty input
- Invalid match ID
- Loading
- OpenDota API error
- Match found
- Backend unavailable

### New Review: Player Selection

Route:

```text
/match/[match_id]/players
```

Purpose:

- Show all 10 players
- Let user choose which player to review

Page content:

- Match summary strip with match ID, duration, and Radiant/Dire result
- Radiant player group
- Dire player group
- Player cards for all 10 players

Each player card:

```text
Juggernaut
Radiant
Lost
KDA: 8 / 7 / 11
GPM: 512

[Review This Player]
```

Useful fields:

- Hero image
- Hero name
- Team
- Result
- KDA
- GPM
- Player slot
- Optional role or lane if available

States:

- Loading players
- Match not found
- OpenDota API error
- Missing hero image, using a fallback
- Anonymous or incomplete player data
- Less than 10 players returned, with a clear incomplete-data note

### New Review: Report

Route:

```text
/match/[match_id]/report/[player_slot]
```

Purpose:

- Display the generated coaching report
- Save the report locally after generation

Layout order:

1. Match Summary
2. Main Thing To Fix
3. Performance Cards
4. Top 3 Mistakes
5. What You Did Well
6. Next 3 Games Training Plan
7. Collapsible Match Evidence
8. AI Limitation Note

Match Summary should show:

- Hero
- Result
- Duration
- KDA
- GPM
- XPM
- Last hits
- Deaths

Main Thing To Fix should show:

- One clear coaching priority
- One or two evidence points supporting it
- Plain language advice for the next game

Performance Cards should show:

- Farming
- Fighting
- Survival
- Objectives

Each mistake should show:

- Title
- What happened
- Evidence
- Why it matters
- Try next game

Additional actions:

- Analyze Another Match
- Back to Players
- Open Saved Reports

States:

- Generating report
- Report generated
- Report validation failed
- AI service unavailable
- Missing evidence, where the wording should become softer or the claim should be omitted
- Report visible but local save failed
- Report saved successfully

### Saved Reports List

Route:

```text
/reports
```

Purpose:

- Let the user reopen reports saved on the local machine

Each saved report row or card:

```text
Juggernaut
Match: 8123456789
Lost
KDA: 8 / 7 / 11
GPM: 512

Main thing to fix:
You fought too early before your farming item.

Confidence: Medium

[Open Report]
```

Useful fields:

- Report ID
- Match ID
- Hero
- Result
- Created date
- KDA
- GPM
- Main problem
- Confidence

States:

- Empty saved reports
- Loading saved reports
- Saved reports loaded
- Storage error
- Report row with missing optional fields

### Saved Report Detail

Route:

```text
/reports/[report_id]
```

Purpose:

- Display a previously saved coaching report

Layout:

- Use the same report layout as `/match/[match_id]/report/[player_slot]`
- Show a small saved-report label with created date
- Include Analyze Another Match and Back to Saved Reports actions

States:

- Loading saved report
- Report not found
- Storage error
- Saved report loaded

## 8. Visual Design Direction

Style:

- Simple dashboard
- Clean spacing
- Easy to scan
- No heavy landing page
- No complicated charts in MVP

Color usage:

- Neutral background
- Green accent for good
- Red accent for risky or needs work
- Gold accent for farming or item timing
- Blue or gray for neutral information

UI language:

- Friendly
- Direct
- Helpful
- Not too technical
- Not too harsh

## 9. Technical Architecture

MVP architecture:

```text
Next.js Frontend
    |
FastAPI Backend
    |
OpenDota API
    |
Analyzer Service
    |
AI Coach Service
    |
SQLite locally / Supabase Postgres in production
```

Recommended stack:

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Pydantic, httpx
- AI: one structured-output AI call
- Database: SQLite locally and Supabase Postgres in production
- Data source: OpenDota
- Tests: pytest for backend logic

## 10. Backend Services

Suggested folder structure:

```text
backend/
  app/
    main.py
    api/
      matches.py
      reports.py
    services/
      opendota.py
      analyzer.py
      coach.py
      storage.py
    schemas/
      match.py
      report.py
    tests/
      test_analyzer.py
      test_report_schema.py
```

Service responsibilities:

- `opendota.py`: fetch match data
- `analyzer.py`: calculate metrics from raw match data
- `coach.py`: generate coaching report
- `storage.py`: save and load reports
- `report.py`: define structured report schema

## 11. API Endpoints

MVP endpoints:

Private retention endpoints:

```text
GET /me/dashboard
GET /me/reports
GET /me/reports/{report_id}
GET /me/recent-matches
GET /me/matches/{match_id}/review-context
POST /me/reports
PUT /me/reports/{report_id}/feedback
POST /sessions/logout
POST /auth/steam/start
GET /auth/steam/callback
```

The frontend stores a random session token in an HttpOnly cookie. FastAPI stores only its hash, owns every report by profile, and upgrades a guest profile after verified Steam OpenID.

```text
GET /health
```

Returns backend status.

```text
GET /matches/{match_id}
```

Fetches and normalizes match data.

```text
GET /matches/{match_id}/players
```

Returns the 10 players in simple UI-friendly format.

Each player should include:

- Hero name
- Hero image URL or image key
- Team
- Result
- KDA
- GPM
- Player slot
- Optional role or lane if available

```text
POST /reports
```

Body:

```json
{
  "match_id": 8123456789,
  "player_slot": 0
}
```

Generates, validates, saves, and returns a structured coaching report.

Important behavior:

- Calculate metrics before calling the AI coach.
- Require evidence for each major coaching claim.
- Save the report locally after successful validation.
- If local saving fails, return the report with a save warning instead of hiding the generated report.

```text
GET /reports
```

Returns saved reports in list-friendly format.

Each saved report item should include:

- Report ID
- Match ID
- Player slot
- Hero
- Result
- Created date
- KDA
- GPM
- Main problem
- Confidence

```text
GET /reports/{report_id}
```

Returns a saved report.

## 12. Metrics To Calculate

Basic metrics:

- Hero
- Team
- Win/loss
- Duration
- Kills
- Deaths
- Assists
- KDA
- GPM
- XPM
- Last hits
- Denies
- Hero damage
- Tower damage
- Healing
- Level

Useful derived metrics:

- Deaths before 10 minutes
- Deaths before 20 minutes
- Kill participation
- Objective contribution
- Farming quality estimate
- Survival risk estimate

Optional if OpenDota provides enough data:

- Item purchase timings
- Lane role
- Lane efficiency
- Teamfight participation

## 13. Coaching Rules

Use simple rule-based evidence before asking the AI to write the final report.

Carry:

- If low last hits and low GPM, mention farming efficiency.
- If many deaths before first major item, mention unsafe farming or early fighting.
- If high kills but low tower damage, mention poor objective conversion.

Support:

- If low wards/sentries, mention vision contribution.
- If many deaths but high assists, be careful before calling it bad.
- If low net worth but good participation, avoid harsh criticism.

Core roles:

- If high hero damage but loss, check objective damage.
- If strong KDA but low tower damage, mention conversion problem.

Important:

- Do not overclaim.
- Always connect advice to evidence.
- Include limitations when data is incomplete.

## 14. AI Prompt Goal

The AI should behave like a calm Dota coach.

It should:

- Use simple language
- Explain one main issue clearly
- Give evidence
- Give practical next-game actions
- Avoid toxic or insulting feedback
- Avoid claims not supported by match data

It should not:

- Pretend to know exact positioning without replay data
- Blame teammates
- Give vague advice only
- Use overly complex analytics language

## 15. Test Plan

Backend tests:

- Analyzer calculates KDA, GPM, XPM, deaths, and derived metrics correctly.
- Report schema accepts valid structured reports.
- Report schema rejects missing required fields.
- Report saving and loading works with SQLite.
- Saved report list returns list-friendly fields.

UI scenarios:

- Match input supports empty, invalid, loading, success, and OpenDota error states.
- Player selection shows 10 players grouped by Radiant and Dire.
- Player cards handle missing hero images and incomplete player data.
- Report page renders all required coaching sections.
- Every mistake includes evidence, or the claim is softened or omitted.
- Saved Reports supports empty, loading, loaded, and storage error states.
- Saved report detail opens a locally saved report by report ID.

Report quality checks:

- Factuality: report matches the actual data.
- Grounding: each mistake includes evidence.
- Usefulness: advice can be applied next game.
- Clarity: language is simple.
- Safety: report avoids unsupported claims and toxic feedback.

## 16. Implementation Tasks

Local MVP tasks:

- Create FastAPI backend
- Add OpenDota match fetcher
- Normalize player data
- Add basic analyzer
- Add structured report schema
- Add simple AI coach generation
- Add local report saving
- Create Next.js UI
- Add simple sidebar navigation
- Add match input page
- Add player selection page
- Add report page
- Add saved reports list page
- Add saved report detail page
- Add backend tests for analyzer, schema, and storage

## 17. Risks And Mitigations

Risk:

- OpenDota data may be incomplete.

Mitigation:

- Show limitation notes.
- Use only available evidence.

Risk:

- AI may hallucinate.

Mitigation:

- Use structured outputs.
- Validate required report fields.
- Require evidence for each mistake.

Risk:

- Advice may be too generic.

Mitigation:

- Build rule-based evidence first.
- Ask AI to explain based only on supplied metrics.

Risk:

- Scope becomes too large.

Mitigation:

- Build post-match MVP only.
- Keep the first version limited to match review, player selection, report display, and saved reports.

## 18. Final MVP Definition

The MVP is complete when:

- The app runs locally.
- User can enter a match ID.
- Backend fetches match data from OpenDota.
- User can select a player.
- Backend calculates basic performance metrics.
- AI returns a structured coaching report.
- UI displays the report in simple daily language.
- Each major claim includes evidence.
- The report includes a practical training plan.
- The report is saved locally after generation.
- User can view a list of saved reports.
- User can reopen a saved report.
