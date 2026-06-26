"""
Server — FastAPI + HTML dashboard + multi-account auto-rotation
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.state import state
from app.engine import (
    make_client, create_account, verify_account,
    scrape_members, run_pipeline_with_all_accounts,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# ─── Helper: load accounts from env ──────────────────────────────────────────
def load_accounts() -> list:
    """Load accounts from ACCOUNTS_JSON env var."""
    try:
        return json.loads(settings.ACCOUNTS_JSON)
    except (json.JSONDecodeError, TypeError):
        return []


def save_accounts(accounts: list):
    """Save accounts back to env (in-memory only for this session)."""
    import os
    os.environ["ACCOUNTS_JSON"] = json.dumps(accounts)
    settings.ACCOUNTS_JSON = json.dumps(accounts)


# ─── Check token ─────────────────────────────────────────────────────────────
def check_token(token: str):
    if token != settings.DASHBOARD_TOKEN:
        raise HTTPException(401, "Invalid token")


# ─── Daily pipeline ──────────────────────────────────────────────────────────
async def do_daily_job():
    """Called by scheduler or /run-now."""
    logger.info("=== DAILY JOB START ===")
    state.last_run = datetime.utcnow().isoformat()

    accounts = load_accounts()
    if not accounts:
        state.last_run_status = "no_accounts"
        state.last_error = "No accounts configured"
        logger.error(state.last_error)
        return

    if not settings.SOURCE_GROUP or not settings.TARGET_GROUP:
        state.last_run_status = "config_error"
        state.last_error = "SOURCE_GROUP or TARGET_GROUP not set"
        logger.error(state.last_error)
        return

    try:
        result = await run_pipeline_with_all_accounts(
            accounts=accounts,
            daily_limit=settings.DAILY_LIMIT_PER_ACCOUNT,
            source_group=settings.SOURCE_GROUP,
            target_group=settings.TARGET_GROUP,
            max_members=settings.MAX_MEMBERS_PER_RUN,
            min_delay=settings.MIN_DELAY,
            max_delay=settings.MAX_DELAY,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
        )
        logger.info(f"Daily job done: {result}")
    except Exception as e:
        state.last_run_status = "error"
        state.last_error = str(e)[:200]
        logger.exception("Daily job failed")


# ─── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loaded {len(load_accounts())} accounts from env")

    sched_hour, sched_min = map(int, settings.SCHEDULE_TIME.split(":"))
    scheduler.add_job(do_daily_job, "cron", hour=sched_hour, minute=sched_min, id="daily")
    scheduler.start()
    logger.info(f"Scheduled daily at {settings.SCHEDULE_TIME} UTC")

    yield
    scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── HTML Dashboard ──────────────────────────────────────────────────────────
DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TG Multi-Account Tool</title>
<style>
  :root { --bg: #0f0f13; --card: #1a1a24; --accent: #6c5ce7; --green: #00b894; --red: #e17055; --text: #dfe6e9; --muted: #636e72; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 2rem 1rem; display:flex; justify-content:center; }
  .container { max-width: 700px; width: 100%; }
  h1 { font-size:1.5rem; font-weight:700; }
  .subtitle { color:var(--muted); font-size:.85rem; margin-bottom:1.5rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:.5rem; }
  .card { background:var(--card); border-radius:14px; padding:1.25rem; margin-bottom:1rem; border:1px solid #2d2d3d; }
  .card h2 { font-size:.95rem; color:var(--accent); margin-bottom:.75rem; display:flex; align-items:center; gap:.5rem; }
  .stat-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:.5rem; }
  .stat { background:rgba(108,92,231,.06); border-radius:10px; padding:.6rem; }
  .stat .lbl { font-size:.7rem; color:var(--muted); text-transform:uppercase; }
  .stat .val { font-size:1.3rem; font-weight:700; margin-top:.1rem; }
  .badge { display:inline-block; padding:.15rem .5rem; border-radius:20px; font-size:.7rem; font-weight:600; }
  .badge-ok { background:rgba(0,184,148,.15); color:var(--green); }
  .badge-err { background:rgba(225,112,85,.15); color:var(--red); }
  .badge-warn { background:rgba(253,203,110,.15); color:#fdcb6e; }
  .btn { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1.2rem; border:none; border-radius:8px; font-size:.85rem; font-weight:600; cursor:pointer; transition:all .15s; text-decoration:none; }
  .btn:hover { filter:brightness(1.12); transform:translateY(-1px); }
  .btn-primary { background:var(--accent); color:#fff; }
  .btn-outline { background:transparent; color:var(--text); border:1px solid #2d2d3d; }
  .btn-success { background:var(--green); color:#fff; }
  .btn-danger { background:var(--red); color:#fff; }
  .btn-sm { padding:.35rem .8rem; font-size:.8rem; }
  table { width:100%; border-collapse:collapse; font-size:.85rem; }
  th { text-align:left; color:var(--muted); font-weight:600; padding:.4rem .3rem; border-bottom:1px solid #2d2d3d; }
  td { padding:.4rem .3rem; border-bottom:1px solid #1a1a24; }
  .loader { display:inline-block; width:14px; height:14px; border:2px solid var(--muted); border-top-color:var(--accent); border-radius:50%; animation:spin .6s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  input,select { width:100%; padding:.5rem .7rem; background:rgba(255,255,255,.04); border:1px solid #2d2d3d; border-radius:7px; color:var(--text); font-size:.85rem; }
  input:focus { outline:none; border-color:var(--accent); }
  label { font-size:.75rem; color:var(--muted); display:block; margin-bottom:.25rem; }
  .flex { display:flex; gap:.5rem; flex-wrap:wrap; align-items:end; }
  .flex-grow { flex:1; }
  .toast { background:var(--card); border:1px solid var(--accent); border-radius:10px; padding:.7rem 1rem; margin-bottom:1rem; display:none; font-size:.85rem; }
  .toast.show { display:block; }
  .toast.err { border-color:var(--red); }
  .toast.ok { border-color:var(--green); }
  .hint { font-size:.75rem; color:var(--muted); margin-top:.25rem; }
  details summary { cursor:pointer; color:var(--accent); font-size:.85rem; padding:.3rem 0; }
  details { margin-top:.5rem; }
</style>
</head>
<body>
<div class="container">

<div class="subtitle">
  <span><h1 style="display:inline">📡 TG Multi-Account</h1> <span id="acc-count" class="badge badge-ok">0 accounts</span></span>
  <span id="status-badge" class="badge badge-warn">● Loading...</span>
</div>

<div id="toast" class="toast"></div>

<!-- Stats -->
<div class="card">
  <h2>📊 Overview</h2>
  <div class="stat-grid">
    <div class="stat"><div class="lbl">Added today</div><div class="val" id="total-today" style="color:var(--accent)">0</div></div>
    <div class="stat"><div class="lbl">All time</div><div class="val" id="total-alltime" style="color:var(--green)">0</div></div>
    <div class="stat"><div class="lbl">Active accounts</div><div class="val" id="active-acc">0</div></div>
  </div>
</div>

<!-- Account table -->
<div class="card">
  <h2>👤 Accounts</h2>
  <div style="overflow-x:auto"><table>
    <thead><tr><th>Phone</th><th>Today</th><th>Limit</th><th>Left</th><th>Status</th></tr></thead>
    <tbody id="accounts-tbody">
      <tr><td colspan="5" style="color:var(--muted);text-align:center">No accounts loaded</td></tr>
    </tbody>
  </table></div>
</div>

<!-- Run & Schedule -->
<div class="card">
  <h2>▶ Run</h2>
  <div class="flex">
    <div class="flex-grow" style="min-width:120px">
      <label>Schedule time (UTC)</label>
      <input type="time" id="sched-time" value="09:00">
    </div>
    <div class="flex-grow" style="min-width:120px">
      <label>Max members per run</label>
      <input type="number" id="max-members" value="300" min="50" step="50">
    </div>
  </div>
  <div class="flex" style="margin-top:.6rem">
    <button class="btn btn-primary" onclick="runNow()">▶ Run Now</button>
    <button class="btn btn-outline" onclick="fetchState()">🔄 Refresh</button>
  </div>
  <div id="run-loader" style="display:none;margin-top:.5rem"><span class="loader"></span> Running...</div>
</div>

<!-- Config -->
<div class="card">
  <h2>⚙️ Config</h2>
  <div class="flex">
    <div class="flex-grow"><label>Source group</label><input type="text" id="src-grp" placeholder="@source OR invite link"></div>
    <div class="flex-grow"><label>Target group</label><input type="text" id="tgt-grp" placeholder="@yourGroup"></div>
  </div>
  <div class="flex" style="margin-top:.6rem">
    <div style="flex:1;min-width:100px"><label>Daily limit / account</label><input type="number" id="daily-limit" value="35" min="10" max="50"></div>
  </div>
  <button class="btn btn-outline btn-sm" style="margin-top:.6rem" onclick="saveConfig()">💾 Save Config</button>
</div>

<!-- CREATE NEW ACCOUNT -->
<div class="card">
  <h2>➕ Create New Account</h2>
  <div class="flex">
    <div class="flex-grow"><label>Phone number</label><input type="text" id="new-phone" placeholder="+1234567890"></div>
    <div><button class="btn btn-primary btn-sm" onclick="sendCode()" style="margin-top:1.2rem">📱 Send Code</button></div>
  </div>
  <div class="flex" style="margin-top:.5rem">
    <div class="flex-grow"><label>Verification code (from Telegram)</label><input type="text" id="new-code" placeholder="12345"></div>
    <div class="flex-grow"><label>2FA password (if any)</label><input type="password" id="new-2fa" placeholder=""></div>
    <div><button class="btn btn-success btn-sm" onclick="verifyCode()" style="margin-top:1.2rem">🔓 Verify</button></div>
  </div>
  <div id="create-result" style="margin-top:.5rem;font-size:.8rem;color:var(--muted);word-break:break-all"></div>
</div>

<!-- BUY NUMBER FROM SMS-ACTIVATE -->
<div class="card">
  <h2>🛒 Auto-Buy Number (SMS-Activate)</h2>
  <div class="flex">
    <div class="flex-grow" style="min-width:150px">
      <label>SMS-Activate API Key</label>
      <input type="password" id="sms-api" placeholder="from sms-activate.org">
    </div>
    <div style="min-width:100px">
      <label>Country</label>
      <select id="sms-country">
        <option value="22">India</option>
        <option value="16">Indonesia</option>
        <option value="6">Vietnam</option>
        <option value="12">Philippines</option>
        <option value="1">Russia</option>
        <option value="14">Brazil</option>
        <option value="3">UK</option>
      </select>
    </div>
    <div><button class="btn btn-success btn-sm" onclick="buyNumber()" style="margin-top:1.2rem">💲 Buy & Create</button></div>
  </div>
  <div class="hint">Auto-buys number, requests Telegram code, and creates account. You just enter the SMS code.</div>
  <div id="buy-result" style="margin-top:.5rem;font-size:.8rem;color:var(--muted)"></div>
</div>

<!-- Last run -->
<div class="card">
  <h2>📋 Last Run</h2>
  <div id="last-run-info" style="font-size:.85rem;margin-bottom:.3rem">Never</div>
  <pre id="log-box" style="background:#0a0a0e;border-radius:7px;padding:.6rem;font-size:.75rem;max-height:150px;overflow-y:auto;color:var(--muted);white-space:pre-wrap"></pre>
</div>

</div>

<script>
const TOKEN = "___TOKEN___";

function toast(msg, type="") {
  const t = document.getElementById("toast");
  t.textContent = msg; t.className = "toast show " + type;
  setTimeout(() => t.classList.remove("show"), 4000);
}

async function api(path, opts={}) {
  const res = await fetch(path, {
    headers: {"Content-Type":"application/json","X-Token":TOKEN,...opts.headers},
    ...opts,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail||data.message||res.statusText);
  return data;
}

async function fetchState() {
  try {
    const d = await api("/api/state");
    document.getElementById("total-today").textContent = d.total_added_today||0;
    document.getElementById("total-alltime").textContent = d.total_all_time||0;
    document.getElementById("active-acc").textContent = d.active_accounts||0;
    document.getElementById("acc-count").textContent = (d.active_accounts||0)+" accounts";
    if (d.source_group) document.getElementById("src-grp").value = d.source_group;
    if (d.target_group) document.getElementById("tgt-grp").value = d.target_group;
    if (d.schedule_time) document.getElementById("sched-time").value = d.schedule_time;
    if (d.daily_limit_per_account) document.getElementById("daily-limit").value = d.daily_limit_per_account;

    // Accounts table
    const tb = document.getElementById("accounts-tbody");
    if (d.accounts && d.accounts.length) {
      tb.innerHTML = d.accounts.map(a => `
        <tr>
          <td>${a.phone||"?"}</td>
          <td>${a.added_today||0}</td>
          <td>${a.daily_limit||35}</td>
          <td style="color:${a.remaining>0?'var(--green)':'var(--red)'}">${a.remaining||0}</td>
          <td><span class="badge ${a.can_add?'badge-ok':'badge-err'}">${a.can_add?'Active':'Full'}</span></td>
        </tr>`).join("");
    } else {
      tb.innerHTML = '<tr><td colspan="5" style="color:var(--muted);text-align:center">No accounts</td></tr>';
    }

    // Last run
    const info = document.getElementById("last-run-info");
    if (d.last_run && d.last_run !== "never") {
      const st = d.last_run_status==="ok"?'<span class="badge badge-ok">OK</span>':'<span class="badge badge-err">FAILED</span>';
      info.innerHTML = `Last: ${new Date(d.last_run+"Z").toLocaleString()} ${st}`;
      if (d.last_error) info.innerHTML += `<br><span style="color:var(--red);font-size:.8rem">${d.last_error}</span>`;
    }
    const bg = document.getElementById("status-badge");
    if (d.last_run_status==="ok"){bg.className="badge badge-ok";bg.textContent="✓ Running"}
    else if(d.last_run_status==="error"||d.last_run_status==="failed"){bg.className="badge badge-err";bg.textContent="✗ Error"}
    else{bg.className="badge badge-warn";bg.textContent="○ Idle"}
  } catch(e) { toast("State error: "+e.message,"err"); }
}

async function runNow() {
  document.getElementById("run-loader").style.display="block";
  try {
    const r = await api("/api/run-now", {method:"POST"});
    document.getElementById("log-box").textContent = JSON.stringify(r,null,2);
    toast(`Added ${r.total_added||0} members using ${r.accounts_used||0} accounts`, r.total_added>0?"ok":"err");
    await fetchState();
  } catch(e) { toast("Run failed: "+e.message,"err"); }
  document.getElementById("run-loader").style.display="none";
}

async function saveConfig() {
  try {
    await api("/api/config", {method:"POST", body: JSON.stringify({
      source_group: document.getElementById("src-grp").value,
      target_group: document.getElementById("tgt-grp").value,
      schedule_time: document.getElementById("sched-time").value,
      max_members: parseInt(document.getElementById("max-members").value),
      daily_limit: parseInt(document.getElementById("daily-limit").value),
    })});
    toast("Config saved!","ok");
  } catch(e) { toast("Save failed: "+e.message,"err"); }
}

// ─── Create account manually ───
async function sendCode() {
  const phone = document.getElementById("new-phone").value;
  if(!phone){toast("Enter phone number","err");return}
  try {
    const r = await api("/api/account/create", {method:"POST", body:JSON.stringify({phone})});
    document.getElementById("create-result").textContent = "✅ Code sent to "+phone;
    toast("Code sent!","ok");
  } catch(e) { toast("Failed: "+e.message,"err"); }
}

async function verifyCode() {
  const phone = document.getElementById("new-phone").value;
  const code = document.getElementById("new-code").value;
  const pass = document.getElementById("new-2fa").value;
  if(!phone||!code){toast("Enter phone and code","err");return}
  try {
    const r = await api("/api/account/verify", {method:"POST", body:JSON.stringify({phone,code,password:pass})});
    document.getElementById("create-result").textContent = "✅ Account added! Session saved.";
    toast(`Account ${phone} ready!`,"ok");
    await fetchState();
  } catch(e) { toast("Verify failed: "+e.message,"err"); }
}

// ─── Buy number from SMS-Activate ───
async function buyNumber() {
  const apiKey = document.getElementById("sms-api").value;
  const country = document.getElementById("sms-country").value;
  if(!apiKey){toast("Enter SMS-Activate API key","err");return}
  const box = document.getElementById("buy-result");
  box.innerHTML = '<span class="loader"></span> Buying number...';
  try {
    const r = await api("/api/account/buy-number", {method:"POST", body:JSON.stringify({api_key:apiKey, country:parseInt(country)})});
    if(r.status === "waiting_code") {
      box.innerHTML = `📱 Number: ${r.phone_number}<br>✅ Code requested from Telegram<br>Enter the SMS code in the "Verification code" field above and click Verify`;
      document.getElementById("new-phone").value = r.phone_number;
      toast("Code sent to SMS-Activate! Check dashboard","ok");
    } else {
      box.textContent = JSON.stringify(r);
    }
  } catch(e) { box.innerHTML = "❌ "+e.message; toast("Buy failed: "+e.message,"err"); }
}

// Poll
fetchState();
setInterval(fetchState, 8000);
</script>
</body>
</html>
"""


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "accounts": len(load_accounts())}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.query_params.get("token", "")
    if token != settings.DASHBOARD_TOKEN:
        return HTMLResponse(f"""<!DOCTYPE html><html><body style="background:#0f0f13;color:#dfe6e9;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif">
<form method="get" style="background:#1a1a24;padding:2rem;border-radius:14px">
  <h2 style="margin:0 0 1rem">🔐 Dashboard</h2>
  <input name="token" placeholder="Enter token" style="padding:.5rem;width:100%;margin-bottom:1rem;background:#2d2d3d;border:none;border-radius:7px;color:white">
  <button style="padding:.5rem 1rem;background:#6c5ce7;color:white;border:none;border-radius:7px;cursor:pointer">Enter</button></form></body></html>""")
    return HTMLResponse(DASHBOARD_HTML.replace("___TOKEN___", settings.DASHBOARD_TOKEN))


@app.get("/api/state")
async def api_state(request: Request):
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    s = state.to_dict(settings.DAILY_LIMIT_PER_ACCOUNT)
    s["source_group"] = settings.SOURCE_GROUP
    s["target_group"] = settings.TARGET_GROUP
    s["schedule_time"] = settings.SCHEDULE_TIME
    s["max_members"] = settings.MAX_MEMBERS_PER_RUN
    s["daily_limit_per_account"] = settings.DAILY_LIMIT_PER_ACCOUNT
    accounts = load_accounts()
    s["total_accounts_configured"] = len(accounts)
    s["logged_in_accounts"] = len(accounts)
    return s


@app.post("/api/run-now")
async def api_run_now(request: Request):
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    accounts = load_accounts()
    if not accounts:
        raise HTTPException(400, "No accounts configured")
    await do_daily_job()
    return state.to_dict(settings.DAILY_LIMIT_PER_ACCOUNT)


@app.post("/api/config")
async def api_config(request: Request):
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    body = await request.json()
    if "source_group" in body and body["source_group"]:
        settings.SOURCE_GROUP = body["source_group"]
    if "target_group" in body and body["target_group"]:
        settings.TARGET_GROUP = body["target_group"]
    if "schedule_time" in body:
        h, m = map(int, body["schedule_time"].split(":"))
        scheduler.reschedule_job("daily", trigger="cron", hour=h, minute=m)
        settings.SCHEDULE_TIME = body["schedule_time"]
    if "max_members" in body:
        settings.MAX_MEMBERS_PER_RUN = int(body["max_members"])
    if "daily_limit" in body:
        settings.DAILY_LIMIT_PER_ACCOUNT = int(body["daily_limit"])
    return {"status": "ok"}


# ─── Account management ──────────────────────────────────────────────────────
@app.post("/api/account/create")
async def api_account_create(request: Request):
    """Step 1: send code to phone number."""
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    body = await request.json()
    phone = body.get("phone", "")
    if not phone:
        raise HTTPException(400, "Phone required")

    client = make_client("", settings.API_ID, settings.API_HASH)
    try:
        result = await create_account(client, phone, settings.API_ID, settings.API_HASH)
        return result
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/account/verify")
async def api_account_verify(request: Request):
    """Step 2: verify code, save session string."""
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    body = await request.json()
    phone = body.get("phone", "")
    code = body.get("code", "")
    password = body.get("password", "")
    if not phone or not code:
        raise HTTPException(400, "Phone and code required")

    client = make_client("", settings.API_ID, settings.API_HASH)
    try:
        result = await verify_account(client, phone, code, password)
        if result.get("status") == "ok" and result.get("session_string"):
            # Save to accounts
            accounts = load_accounts()
            # Remove existing entry for this phone if any
            accounts = [a for a in accounts if a.get("phone") != phone]
            accounts.append({
                "phone": phone,
                "session": result["session_string"],
            })
            save_accounts(accounts)
            state.get_account(phone)  # initialize state
            return {"status": "ok", "message": f"Account {phone} added", "accounts_total": len(accounts)}
        return result
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/account/buy-number")
async def api_account_buy_number(request: Request):
    """
    Buy a number from SMS-Activate, request Telegram code.
    Returns phone_number. User then enters the SMS code manually.
    """
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    body = await request.json()
    api_key = body.get("api_key", "")
    country = body.get("country", 22)  # default India

    if not api_key:
        raise HTTPException(400, "API key required")

    import httpx

    try:
        # Step 1: Get number
        async with httpx.AsyncClient() as http:
            resp = await http.get(
                "https://api.sms-activate.org/stubs/handler_api.php",
                params={
                    "api_key": api_key,
                    "action": "getNumber",
                    "service": "tg",
                    "country": country,
                }
            )
            text = resp.text.strip()
            if text.startswith("ACCESS_NUMBER:"):
                parts = text.split(":")
                activation_id = parts[1]
                phone = parts[2]
            else:
                raise HTTPException(400, f"SMS-Activate error: {text}")

            # Step 2: Set status to ready (we'll receive the SMS)
            await http.get(
                "https://api.sms-activate.org/stubs/handler_api.php",
                params={
                    "api_key": api_key,
                    "action": "setStatus",
                    "id": activation_id,
                    "status": "1",  # ready
                }
            )

        # Step 3: Create Telegram client and send code to this number
        client = make_client("", settings.API_ID, settings.API_HASH)
        sent = await create_account(client, phone, settings.API_ID, settings.API_HASH)

        # Store activation ID for later status check
        return {
            "status": "waiting_code",
            "phone_number": phone,
            "activation_id": activation_id,
            "message": "Code sent. Check SMS-Activate dashboard for the code, then enter it above.",
        }

    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/account/buy-number/check")
async def api_check_sms(request: Request):
    """Check if SMS arrived on SMS-Activate activation."""
    token = request.headers.get("X-Token","") or request.query_params.get("token","")
    check_token(token)
    body = await request.json()
    api_key = body.get("api_key", "")
    activation_id = body.get("activation_id", "")

    if not api_key or not activation_id:
        raise HTTPException(400, "API key and activation ID required")

    import httpx

    async with httpx.AsyncClient() as http:
        resp = await http.get(
            "https://api.sms-activate.org/stubs/handler_api.php",
            params={
                "api_key": api_key,
                "action": "getStatus",
                "id": activation_id,
            }
        )
        text = resp.text.strip()
        if text.startswith("STATUS_OK"):
            code = text.split(":")[1] if ":" in text else ""
            return {"status": "received", "code": code}
        return {"status": "waiting", "message": text}


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.server:app", host=settings.HOST, port=settings.PORT, log_level="info")
