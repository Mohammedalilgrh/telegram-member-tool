# Telegram Member Tool — Multi-Account Auto-Rotation

**Deploy on Render (free) + UptimeRobot (free) = runs 24/7**

## 💡 How It Works

1. **Buy cheap temp numbers** from SMS-Activate ($0.10-0.30 each)
2. **Create Telegram accounts** from the dashboard (enter code once, done)
3. **Session strings are saved** — numbers expire but accounts live forever
4. **Tool rotates across all accounts** — each adds 35/day
5. **10 accounts × 35/day = 350/day** for ~$3 one-time

## 🚀 5-Minute Deploy

### 1. Deploy on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect repo → **Build:** `pip install -r requirements.txt` → **Start:** `uvicorn app.server:app --host 0.0.0.0 --port $PORT`
4. Add env vars:

| Variable | Value |
|---|---|
| `TG_API_ID` | From [my.telegram.org/apps](https://my.telegram.org/apps) |
| `TG_API_HASH` | From my.telegram.org |
| `DASHBOARD_TOKEN` | Pick a secret password |
| `SOURCE_GROUP` | `@groupToScrapeFrom` |
| `TARGET_GROUP` | `@yourTargetGroup` |
| `DAILY_LIMIT` | `35` |
| `MAX_MEMBERS` | `200` |

5. Deploy

### 2. Keep Alive with UptimeRobot

1. [uptimerobot.com](https://uptimerobot.com) → **New Monitor**
2. Type: **HTTP(s)** → URL: `https://your-app.onrender.com/health`
3. Interval: **5 minutes**

### 3. Add Accounts via Dashboard

1. Open `https://your-app.onrender.com/?token=YOUR_TOKEN`
2. Go to **Create New Account** section
3. **Manual method:**
   - Enter phone → **Send Code**
   - Check Telegram app for code → enter it → **Verify**
   - Session saved ✅

4. **Auto-buy method (SMS-Activate):**
   - Get API key from [sms-activate.org](https://sms-activate.org)
   - Select country → **Buy & Create**
   - Tool buys number, requests Telegram code automatically
   - Check SMS-Activate dashboard for code → enter it → **Verify**
   - Session saved ✅

### 4. Run Daily

Click **▶ Run Now** to test. The scheduler runs automatically at your set time.

## 📊 Dashboard

```
┌──────────────────────────────────────┐
│ 📊 Overview                          │
│ Added today: 105   All time: 1420    │
│ Active accounts: 3                   │
├──────────────────────────────────────┤
│ 👤 Accounts                          │
│ Phone         Today  Limit  Left     │
│ +123***8901   35     35     0  Full  │
│ +123***8902   35     35     0  Full  │
│ +123***8903   35     35     0  Full  │
├──────────────────────────────────────┤
│ ▶ Run Now           Daily schedule   │
│ ➕ Create Account (manual)           │
│ 🛒 Auto-Buy Number (SMS-Activate)   │
└──────────────────────────────────────┘
```

## 🔒 Safety

- **35/day per account** — Telegram's safe zone
- **2-5s random delays** between adds
- **FloodWait handler** — respects Telegram exactly
- **Bot/scam/fake filter** — quality users only
- **Accounts isolated** — one ban doesn't affect others

## 💰 Cost Breakdown

| Item | Cost | Frequency |
|---|---|---|
| Render free tier | $0 | Forever |
| UptimeRobot | $0 | Forever |
| SMS-Activate numbers | $0.10-0.30 each | One-time per account |
| **10 accounts** | **~$2-3** | **One-time** |

## Account Limits

| Accounts | Adds/day | Setup cost |
|---|---|---|
| 1 | 35 | $0 (your phone) |
| 3 | 105 | ~$0.60 |
| 5 | 175 | ~$1.00 |
| 10 | 350 | ~$2-3 |
| 20 | 700 | ~$5-6 |
