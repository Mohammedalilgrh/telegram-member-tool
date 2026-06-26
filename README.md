# 📡 Telegram Member Tool — Multi-Account Auto-Add

**🇺🇸 English | 🇸🇦 العربية**

Scrape members from any Telegram group and automatically add them to your group. Supports unlimited accounts — each adds 35 members/day safely. Zero monthly fees.

---
---

## 🇺🇸 ENGLISH — Full Setup Guide

### 🔹 What This Tool Does

```
1. You add one or more Telegram accounts (your phone + virtual numbers)
2. Tool scrapes members from a SOURCE group
3. Filters out bots / scam / fake accounts
4. Automatically adds them to YOUR target group
5. Each account adds 35 members per day (configurable)
6. Rotates between accounts when one hits its limit
7. Resets counters daily at midnight
```

**Example — 10 accounts running daily:**

```
Account 1  → +35 → full
Account 2  → +35 → full
Account 3  → +35 → full
...
Account 10 → +35 → full
────────────────
Total: 350 members added to your group today ✅
```

---

### 🔹 Prerequisites (what you need before starting)

| # | Item | Where to get it |
|---|---|---|
| 1 | **GitHub account** | [github.com](https://github.com) |
| 2 | **Render account** | [render.com](https://render.com) — free |
| 3 | **Telegram API ID + Hash** | [my.telegram.org/apps](https://my.telegram.org/apps) |
| 4 | **A Telegram phone number** | Your own phone, or virtual numbers |

---

### 🔹 Step 1: Get Telegram API Credentials

1. Go to **[my.telegram.org/apps](https://my.telegram.org/apps)**
2. Log in with your phone number
3. You'll see **api_id** and **api_hash** — copy both
4. If you don't see them, click "Create Application"

> ⚠️ Keep these private. Anyone with them can control your Telegram account.

---

### 🔹 Step 2: Deploy on Render (free)

1. Go to **[render.com](https://render.com)** → Sign up (free)
2. Click **New +** → **Web Service**
3. Connect your GitHub → choose `telegram-member-tool`
4. Fill the form:

| Field | Value |
|---|---|
| **Name** | `telegram-member-tool` |
| **Region** | Choose closest to you |
| **Branch** | `master` |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | **Free** |

5. Click **Advanced** → **Add Environment Variables**

### 🔹 Step 3: Set Environment Variables

Add these **one by one** on Render:

| Variable | Value | Required? |
|---|---|---|
| `TG_API_ID` | Your `api_id` from step 1 | ✅ Yes |
| `TG_API_HASH` | Your `api_hash` from step 1 | ✅ Yes |
| `TOKEN` | Make up a password (e.g. `mySecret123`) | ✅ Yes |
| `SOURCE_GROUP` | `@groupYouWantToScrape` or invite link | ✅ Yes |
| `TARGET_GROUP` | `@yourGroupToAddTo` or invite link | ✅ Yes |
| `DAILY_LIMIT` | `35` (safe) | Optional |
| `MAX_MEMBERS` | `300` (max to scrape per run) | Optional |

6. Click **Create Web Service** → Wait 2-3 minutes for build

---

### 🔹 Step 4: Keep Alive with UptimeRobot (free)

Render free web services **sleep after 15 minutes of inactivity**. UptimeRobot pings every 5 minutes to keep it awake.

1. Go to **[uptimerobot.com](https://uptimerobot.com)** → Sign up (free)
2. Click **Add New Monitor**
3. Settings:

| Field | Value |
|---|---|
| **Monitor Type** | `HTTP(s)` |
| **Friendly Name** | `Telegram Tool` |
| **URL (or IP)** | `https://your-app-name.onrender.com/health` |
| **Monitoring Interval** | `Every 5 minutes` |

4. Click **Create Monitor** → Done

---

### 🔹 Step 5: Open Dashboard

1. Open this URL in your browser:

```
https://your-app-name.onrender.com/?token=YOUR_TOKEN
```

Replace `your-app-name` with your Render app name.
Replace `YOUR_TOKEN` with the password you set in env vars.

2. You'll see the dashboard:

```
┌─────────────────────────────────────┐
│ 📡 TG Tool                          │
│ 📊 Stats                            │
│ 👤 Accounts (empty - need to add)    │
│ ▶ Run Now                           │
│ ➕ Add Account (manual)              │
│ 🛒 Auto-Buy Number (SMS-Activate)   │
└─────────────────────────────────────┘
```

---

### 🔹 Step 6: Add Your First Account

#### Method A: Add Your Own Phone (manual)

1. In the **Add Account** section, enter your phone with country code:

```
Example: +1234567890
```

2. Click **Send Code**
3. Open Telegram app → you'll receive a login code
4. Enter the code in the **Code** field → Click **Verify**
5. ✅ Dashboard now shows 1 account connected

#### Method B: Buy a Virtual Number and Create Account (auto)

1. Go to **[sms-activate.org](https://sms-activate.org)** → Sign up
2. Add funds (minimum ~$2-3)
3. Go to **API** section → copy your **API Key**
4. In the dashboard **Auto-Buy** section:
   - Paste your SMS-Activate API key
   - Select a country (India = cheapest, ~$0.10)
   - Click **Buy**
5. Tool buys number → requests Telegram code automatically
6. Check SMS-Activate dashboard for the code
7. Enter the code in the **Verification code** field → Click **Verify**
8. ✅ Account added forever

> 💡 **Important:** You only need the number ONE TIME to receive the SMS code. After that, the session string saves the account permanently. Even after the virtual number expires, your Telegram account works forever.

---

### 🔹 Step 7: Add More Accounts (optional)

Repeat Step 6 for each account you want. Each account adds **35 members/day** independently.

| # Accounts | Cost (one-time) | Daily members added |
|---|---|---|
| 1 (your phone) | $0 | 35 |
| 3 | ~$0.60 | 105 |
| 5 | ~$1.00 | 175 |
| 10 | ~$2-3 | 350 |
| 20 | ~$5-6 | 700 |

---

### 🔹 Step 8: Run

1. Click **▶ Run Now** on the dashboard
2. Tool will:
   - ✅ Scrape members from `SOURCE_GROUP`
   - ✅ Filter bots, scam, fake
   - ✅ Randomize the list
   - ✅ Add members using Account 1 (35 adds)
   - ✅ Switch to Account 2 (35 adds)
   - ✅ Switch to Account 3... until daily limit
3. Results show in the **Last Run** section

**First run? Start with dry run (set DAILY_LIMIT=5) to test.**

---

### 🔹 Automatic Daily Schedule

The tool runs **automatically every day** at the time you set:

| Env Variable | Default | Description |
|---|---|---|
| `SCHEDULE_TIME` | `09:00` | Daily run time (UTC) |

You can also set it from the dashboard config section.

UptimeRobot keeps the server alive 24/7 so the scheduler never misses a run.

---

### 🔹 Dashboard Sections Explained

| Section | What it does |
|---|---|
| **📊 Stats** | Shows today's adds, all-time total, remaining limit |
| **👤 Accounts** | Table of all your accounts with today's count per account |
| **▶ Run** | Click to run the pipeline NOW |
| **⚙️ Config** | Set source group, target group, daily limit, schedule time |
| **➕ Add Account** | Enter phone → receive code → verify → account saved |
| **🛒 Auto-Buy** | Buy virtual number from SMS-Activate and create account |
| **📋 Last Run** | Shows result of last run |

---

### 🔹 Understanding the Safety Limits

| Setting | Default | What it does |
|---|---|---|
| `DAILY_LIMIT` | 35 | Max members this account can add in 24h |
| Hourly limit | 15 (built-in) | Max per hour per account |
| Delay between adds | 2-5 seconds (random) | Looks human, avoids flood detection |

**Why 35?** Telegram allows ~50/day before FloodWait kicks in. 35 is the safe zone that works for months.

**Can I increase it?** Yes. Change `DAILY_LIMIT` to 50 or 70. But expect FloodWaits to eventually appear.

---

### 🔹 How to Check If It's Working

Open the dashboard anytime:

```
https://your-app.onrender.com/?token=YOUR_TOKEN
```

You'll see:
- Today's count going up
- Accounts showing "Active" or "Full"
- Last run status

Also check your target Telegram group → members should increase.

---

### 🔹 FAQ

**Q: Do I need a separate phone for each account?**
A: No. You need the phone number just ONCE to receive the SMS code. After that, the account is saved forever even if the number expires.

**Q: Will my accounts get banned?**
A: At 35/day with 2-5s delays, accounts run for months without issues. Pushing 80-100/day per account will get FloodWaits.

**Q: What if one account gets banned?**
A: Just delete it from the config and add a new one. Other accounts keep working.

**Q: Can I use the same phone number for multiple accounts?**
A: No. Telegram allows 1 account per number. Each account needs its own number.

**Q: How do I get cheap numbers?**
A: SMS-Activate.org — India numbers ~$0.10 each. One-time use for the SMS code.

**Q: Does Render cost money?**
A: No. The free tier works. UptimeRobot keeps it from sleeping.

**Q: Can I run it on my own computer instead of Render?**
A: Yes. Install Python, run `pip install -r requirements.txt`, then `uvicorn app:app --host 0.0.0.0 --port 8000`.

---

### 🔹 Project Files

```
telegram-member-tool/
├── app.py              ← The whole tool (one file)
├── requirements.txt    ← Python dependencies
├── Procfile            ← Render start command
├── render.yaml         ← Render blueprint
├── README.md           ← This file
└── .gitignore
```

---

---

## 🇸🇦 ARABIC — دليل الإعداد الكامل

### 🔹 ماذا تفعل هذه الأداة؟

```
1. تضيف واحد أو أكثر من حسابات تيليجرام (رقمك + أرقام افتراضية)
2. الأداة تسحب الأعضاء من مجموعة SOURCE (المصدر)
3. تصفي البوتات والحسابات المزيفة
4. تضيفهم تلقائياً إلى مجموعتك TARGET (الهدف)
5. كل حساب يضيف 35 عضواً في اليوم (قابل للتعديل)
6. تتنقل بين الحسابات تلقائياً عندما يصل أحدها للحد
7. تعيد ضبط العداد يومياً عند منتصف الليل
```

**مثال — 10 حسابات تعمل يومياً:**

```
الحساب 1  → +35 → اكتمل
الحساب 2  → +35 → اكتمل
الحساب 3  → +35 → اكتمل
...
الحساب 10 → +35 → اكتمل
────────────────
المجموع: 350 عضواً أضيفوا لمجموعتك اليوم ✅
```

---

### 🔹 المتطلبات الأساسية

| # | الشيء | أين تحصل عليه |
|---|---|---|
| 1 | **حساب GitHub** | [github.com](https://github.com) |
| 2 | **حساب Render** | [render.com](https://render.com) — مجاني |
| 3 | **API ID + Hash التيليجرام** | [my.telegram.org/apps](https://my.telegram.org/apps) |
| 4 | **رقم هاتف تيليجرام** | رقمك الخاص أو أرقام افتراضية |

---

### 🔹 الخطوة 1: الحصول على بيانات API من تيليجرام

1. اذهب إلى **[my.telegram.org/apps](https://my.telegram.org/apps)**
2. سجل الدخول برقم هاتفك
3. ستظهر لك **api_id** و **api_hash** — انسخهما
4. إذا لم تظهر، اضغط **Create Application**

> ⚠️ لا تشارك هذه المعلومات مع أي أحد.

---

### 🔹 الخطوة 2: النشر على Render (مجاني)

1. اذهب إلى **[render.com](https://render.com)** → سجل (مجاني)
2. اضغط **New +** → **Web Service**
3. اتصّل بحساب GitHub → اختر `telegram-member-tool`
4. املأ النموذج:

| الحقل | القيمة |
|---|---|
| **Name** | `telegram-member-tool` |
| **Region** | اختر الأقرب لك |
| **Branch** | `master` |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | **Free** |

5. اضغط **Advanced** ← **Add Environment Variables**

### 🔹 الخطوة 3: إضافة متغيرات البيئة

أضف هذه **واحدة تلو الأخرى** على Render:

| المتغير | القيمة | مطلوب؟ |
|---|---|---|
| `TG_API_ID` | `api_id` من الخطوة 1 | ✅ نعم |
| `TG_API_HASH` | `api_hash` من الخطوة 1 | ✅ نعم |
| `TOKEN` | اختر كلمة سر (مثلاً `mySecret123`) | ✅ نعم |
| `SOURCE_GROUP` | `@المجموعة_التي_تسحب_منها` | ✅ نعم |
| `TARGET_GROUP` | `@مجموعتك_التي_تضيف_إليها` | ✅ نعم |
| `DAILY_LIMIT` | `35` (آمن) | اختياري |

6. اضغط **Create Web Service** → انتظر 2-3 دقائق

---

### 🔹 الخطوة 4: إبقاء التطبيق حياً مع UptimeRobot (مجاني)

خدمات Render المجانية **تنام بعد 15 دقيقة من عدم النشاط**. UptimeRobot يرسل إشارة كل 5 دقائق ليبقيه مستيقظاً.

1. اذهب إلى **[uptimerobot.com](https://uptimerobot.com)** → سجل (مجاني)
2. اضغط **Add New Monitor**
3. الإعدادات:

| الحقل | القيمة |
|---|---|
| **Monitor Type** | `HTTP(s)` |
| **Friendly Name** | `Telegram Tool` |
| **URL** | `https://your-app-name.onrender.com/health` |
| **Monitoring Interval** | `Every 5 minutes` |

4. اضغط **Create Monitor** → تم

---

### 🔹 الخطوة 5: فتح لوحة التحكم

1. افتح هذا الرابط في المتصفح:

```
https://your-app-name.onrender.com/?token=YOUR_TOKEN
```

استبدل `your-app-name` باسم تطبيقك على Render.
استبدل `YOUR_TOKEN` بكلمة السر التي اخترتها.

2. ستظهر لوحة التحكم:

```
┌─────────────────────────────────────┐
│ 📡 TG Tool                          │
│ 📊 الإحصائيات                        │
│ 👤 الحسابات                         │
│ ▶ تشغيل الآن                        │
│ ➕ إضافة حساب (يدوي)                 │
│ 🛒 شراء رقم تلقائي (SMS-Activate)   │
└─────────────────────────────────────┘
```

---

### 🔹 الخطوة 6: إضافة حسابك الأول

#### الطريقة أ: إضافة رقمك الشخصي (يدوي)

1. في قسم **Add Account**، أدخل رقم هاتفك مع مفتاح الدولة:

```
مثال: +967123456789
```

2. اضغط **Send Code**
3. افتح تطبيق تيليجرام → ستستلم كود تسجيل الدخول
4. أدخل الكود في حقل **Code** → اضغط **Verify**
5. ✅ لوحة التحكم تظهر الآن حساباً واحداً متصلاً

#### الطريقة ب: شراء رقم افتراضي وإنشاء حساب (تلقائي)

1. اذهب إلى **[sms-activate.org](https://sms-activate.org)** → سجل
2. أضف رصيد (الحد الأدنى ~$2-3)
3. اذهب إلى قسم **API** → انسخ **API Key**
4. في لوحة التحكم قسم **Auto-Buy**:
   - الصق مفتاح API
   - اختر دولة (الهند = الأرخص، ~$0.10)
   - اضغط **Buy**
5. الأداة تشتري رقماً وتطلب كود تيليجرام تلقائياً
6. افحص لوحة تحكم SMS-Activate لترى الكود
7. أدخل الكود في حقل **Verification code** → اضغط **Verify**
8. ✅ تمت إضافة الحساب إلى الأبد

> 💡 **مهم:** تحتاج الرقم **مرة واحدة فقط** لاستلام كود SMS. بعد ذلك، يتم حفظ الحساب بشكل دائم. حتى لو انتهت صلاحية الرقم الافتراضي، حساب تيليجرام الخاص بك يعمل إلى الأبد.

---

### 🔹 الخطوة 7: إضافة المزيد من الحسابات (اختياري)

كرر الخطوة 6 لكل حساب تريده. كل حساب يضيف **35 عضواً في اليوم** بشكل مستقل.

| عدد الحسابات | التكلفة (مرة واحدة) | الأعضاء يومياً |
|---|---|---|
| 1 (رقمك) | $0 | 35 |
| 3 | ~$0.60 | 105 |
| 5 | ~$1.00 | 175 |
| 10 | ~$2-3 | 350 |
| 20 | ~$5-6 | 700 |

---

### 🔹 الخطوة 8: التشغيل

1. اضغط **▶ Run Now** في لوحة التحكم
2. الأداة سوف:
   - ✅ تسحب الأعضاء من `SOURCE_GROUP`
   - ✅ تصفي البوتات والحسابات المزيفة
   - ✅ ترتب القائمة عشوائياً
   - ✅ تضيف أعضاء باستخدام الحساب 1 (35 إضافة)
   - ✅ تنتقل إلى الحساب 2 (35 إضافة)
   - ✅ تنتقل إلى الحساب 3... حتى الحد اليومي
3. النتائج تظهر في قسم **Last Run**

**لأول مرة؟** ابدأ بـ `DAILY_LIMIT=5` للاختبار.

---

### 🔹 الجدول الزمني التلقائي

الأداة تعمل **تلقائياً كل يوم** في الوقت الذي تحدده:

| المتغير | الافتراضي | الشرح |
|---|---|---|
| `SCHEDULE_TIME` | `09:00` | وقت التشغيل اليومي (UTC) |

UptimeRobot يبقي السيرفر شغال 24/7 حتى لا يفوت الجدول الزمني أي تشغيلة.

---

### 🔹 أقسام لوحة التحكم

| القسم | الوظيفة |
|---|---|
| **📊 Stats** | يعرض إضافات اليوم، المجموع الكلي، الحد المتبقي |
| **👤 Accounts** | جدول بجميع حساباتك مع عدد الإضافات لكل حساب |
| **▶ Run** | اضغط لتشغيل المهمة الآن |
| **⚙️ Config** | ضبط مجموعة المصدر، الهدف، الحد اليومي، الوقت |
| **➕ Add Account** | أدخل رقماً → استلم كود → تحقق → حفظ الحساب |
| **🛒 Auto-Buy** | اشترِ رقماً افتراضياً من SMS-Activate وأنشئ حساباً |
| **📋 Last Run** | يعرض نتيجة آخر تشغيل |

---

### 🔹 حدود الأمان

| الإعداد | الافتراضي | ماذا يفعل |
|---|---|---|
| `DAILY_LIMIT` | 35 | أقصى عدد أعضاء يمكن إضافتهم في 24 ساعة |
| الحد الساعي | 15 (مدمج) | أقصى عدد في الساعة لكل حساب |
| التأخير بين الإضافات | 2-5 ثوانٍ (عشوائي) | يبدو طبيعياً لمنع الحظر |

**لماذا 35؟** التيليجرام يسمح بحوالي 50 إضافة في اليوم قبل أن يبدأ FloodWait. 35 هي المنطقة الآمنة التي تعمل لأشهر.

**هل يمكنني زيادتها؟** نعم. غير `DAILY_LIMIT` إلى 50 أو 70. لكن توقع ظهور FloodWait في النهاية.

---

### 🔹 كيف تتأكد أن الأداة تعمل؟

افتح لوحة التحكم في أي وقت:

```
https://your-app-name.onrender.com/?token=YOUR_TOKEN
```

سترى:
- عداد اليوم يرتفع
- الحسابات تظهر "Active" أو "Full"
- حالة آخر تشغيل

أيضاً افحص مجموعة تيليجرام الهدف → يجب أن ترى الأعضاء يزيدون.

---

### 🔹 الأسئلة الشائعة

**س: هل أحتاج هاتف منفصل لكل حساب؟**
ج: لا. تحتاج الرقم **مرة واحدة فقط** لاستلام كود SMS. بعد ذلك، الحساب محفوظ إلى الأبد حتى لو انتهت صلاحية الرقم.

**س: هل سيتم حظر حساباتي؟**
ج: عند 35 إضافة في اليوم مع تأخير 2-5 ثوانٍ، الحسابات تعمل لأشهر بدون مشاكل. الدفع بـ 80-100 في اليوم سيسبب FloodWait.

**س: ماذا لو تم حظر أحد الحسابات؟**
ج: احذفه من الإعدادات وأضف حساباً جديداً. بقية الحسابات تستمر في العمل.

**س: هل يمكنني استخدام نفس الرقم لأكثر من حساب؟**
ج: لا. تيليجرام يسمح بحساب واحد لكل رقم. كل حساب يحتاج رقماً خاصاً به.

**س: كيف أحصل على أرقام رخيصة؟**
ج: SMS-Activate.org — أرقام الهند ~$0.10 لكل رقم. استخدام لمرة واحدة لاستلام كود SMS.

**س: هل Render يكلف مالاً؟**
ج: لا. الباقة المجانية تعمل. UptimeRobot يمنع التطبيق من النوم.

**س: هل يمكنني تشغيله على جهازي بدلاً من Render؟**
ج: نعم. ثبّت Python، شغّل `pip install -r requirements.txt`، ثم `uvicorn app:app --host 0.0.0.0 --port 8000`.

---

### 🔹 ملفات المشروع

```
telegram-member-tool/
├── app.py              ← الأداة كلها (ملف واحد)
├── requirements.txt    ← مكتبات Python
├── Procfile            ← أمر تشغيل Render
├── render.yaml         ← إعدادات Render
├── README.md           ← هذا الملف
└── .gitignore
```
