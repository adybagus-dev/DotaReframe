# DotaReframe MVP UI Prompt

Create a clean, easy-to-read dashboard UI for **DotaReframe**, a post-match Dota 2 review app.

Core flow:

```text
Enter Match ID -> Choose Your Hero -> Read Your Review
```

The app should feel like a calm Dota coach, not a complex analytics tool. Use simple day-by-day language in the UI and report. Avoid technical analytics jargon.

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

## MVP Navigation

Use a simple sidebar with only:

- New Review
- Saved Reports

Sidebar content:

```text
DotaReframe

New Review
Saved Reports

Backend: Online
```

Main content should show a clear page title, short supporting text, and the current screen's main action.

## Screen 1: Match Input

Route: `/match`

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

Useful states:

- Empty input
- Invalid match ID
- Loading
- OpenDota API error
- Match found
- Backend unavailable

## Screen 2: Player Selection

Route: `/match/[match_id]/players`

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
- Missing hero image fallback
- Anonymous or incomplete player data

## Screen 3: Review Report

Route: `/match/[match_id]/report/[player_slot]`

Purpose:

- Display generated coaching report
- Show that report is saved locally

Layout order:

1. Match Summary
2. Main Thing To Fix
3. Performance Cards
4. Top 3 Mistakes
5. What You Did Well
6. Next 3 Games Training Plan
7. Collapsible Match Evidence
8. AI Limitation Note

Match Summary fields:

- Hero
- Result
- Duration
- KDA
- GPM
- XPM
- Last hits
- Deaths

Main Thing To Fix example:

```text
You fought too early before your farming item.
Evidence: 3 deaths before minute 18.
Try next game: Farm safer until your first core item, unless your team is defending a tower.
```

Performance Cards:

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

Actions:

- Analyze Another Match
- Back to Players
- Open Saved Reports

States:

- Generating report
- Report generated
- Report validation failed
- AI service unavailable
- Missing evidence, with softer wording
- Report visible but local save failed
- Report saved successfully

## Screen 4: Saved Reports List

Route: `/reports`

Purpose:

- Let user reopen reports saved on the local machine

Each saved report row/card:

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

## Screen 5: Saved Report Detail

Route: `/reports/[report_id]`

Use the same layout as the Review Report screen.

Add:

- Small saved-report label with created date
- Analyze Another Match action
- Back to Saved Reports action

States:

- Loading saved report
- Report not found
- Storage error
- Saved report loaded

## Visual Style

- Simple dashboard
- Clean spacing
- Easy to scan
- No heavy landing page
- No complicated charts
- Neutral background
- Green accent for good
- Red accent for risky or needs work
- Gold accent for farming or item timing
- Blue or gray for neutral information
- Friendly, direct, helpful language
- Not too technical
- Not too harsh
