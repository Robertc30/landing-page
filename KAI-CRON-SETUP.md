# KAI's Corner Daily Update Cron Job

To add this job manually, run:

```bash
npx openclaw cron add \
  --name "KAI Daily Update" \
  --schedule "0 20 * * *" \
  --tz "America/New_York" \
  --sessionTarget "isolated" \
  --payloadKind "agentTurn" \
  --payloadMessage "cd landing-page && python add-kai-corner.py"
```

## Job Details
- **Name**: KAI Daily Update
- **Schedule**: Daily at 8:00 PM EST
- **Session**: isolated
- **Payload**: cd landing-page && python add-kai-corner.py

## What it does
Runs the KAI corner update script which:
1. Generates daily insights from KAI's perspective
2. Updates the TLDR summary
3. Creates a new blog entry
4. Updates the entries index

## Files created
- `landing-page/kai-corner.html` - Main KAI's Corner page
- `landing-page/kai-corner.js` - Dynamic content loader
- `landing-page/add-kai-corner.py` - Update script
- `landing-page/blog/kai-*.html` - Individual entries
- `landing-page/blog/kai-tldr.json` - Daily summary
- `landing-page/blog/kai-entries.json` - Entries index
- `landing-page/blog/kai-todos.json` - Current todos
