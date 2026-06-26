# Telegram Multi-Account Tool

**One file. Deploy on Render free tier. Dashboard handles everything.**

## Setup (3 minutes)

### 1. Deploy

1. Fork/push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service** → connect repo
3. Set these env vars:

| Variable | Where to get it |
|---|---|
| `TG_API_ID` | [my.telegram.org/apps](https://my.telegram.org/apps) |
| `TG_API_HASH` | from my.telegram.org |
| `TOKEN` | Make up any password |
| `SOURCE_GROUP` | `@groupToScrape` or invite link |
| `TARGET_GROUP` | `@yourGroup` |

4. Deploy

### 2. Keep alive (free)

[uptimerobot.com](https://uptimerobot.com) → Monitor → URL: `https://your-app.onrender.com/health` → 5 min

### 3. Open dashboard

`https://your-app.onrender.com/?token=YOUR_TOKEN`

### 4. Add accounts

- **Manual:** Enter phone → Send Code → enter the code from Telegram → Verify
- **Auto:** Enter SMS-Activate API key → Buy → enter code → Verify

### 5. Click "Run Now"

Done.

## Cost

- **Render:** $0
- **UptimeRobot:** $0
- **SMS-Activate numbers:** $0.10-0.30 each (one-time)

10 accounts → ~$3 → 350 members/day forever
