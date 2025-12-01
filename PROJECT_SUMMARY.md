# 🚀 Dailicle - Complete Custom Server

**Your personal AI article generation system is ready!**

I've built you a complete **Python FastAPI server** that replaces n8n and runs everything locally or on free hosting.

---

## ✨ What You Got

### 🏗️ Complete Server Implementation

```
dailicle/
├── 📄 main.py                    # FastAPI server
├── ⚙️ config.py                   # Environment config
├── ⏰ scheduler.py                # Cron scheduler (daily 6 AM IST)
├── 📦 requirements.txt            # Dependencies
├── 🔐 .env.example               # Config template
│
├── 🎯 api/
│   └── routes.py                 # REST API endpoints
│
├── 🔧 services/
│   ├── llm_service.py           # OpenAI article generation
│   ├── notion_service.py        # Notion page creator
│   ├── email_service.py         # SMTP email sender
│   ├── orchestrator.py          # Workflow coordinator
│   └── storage_service.py       # Local/S3 storage
│
├── 💬 prompts/
│   └── article_prompt.py        # Full LLM prompt
│
├── 📧 templates/
│   └── email_template.html      # Beautiful HTML email
│
└── 🚀 Deployment files
    ├── railway.toml             # Railway.app config
    ├── render.yaml              # Render.com config
    ├── fly.toml                 # Fly.io config
    ├── Procfile                 # Heroku/generic
    └── setup.sh                 # Quick setup script
```

---

## 🎯 Features

✅ **Automatic Daily Generation** - Cron scheduler runs at 6 AM IST  
✅ **OpenAI Integration** - Uses GPT-4o-mini (cost-effective)  
✅ **Notion Pages** - Auto-creates formatted subpages  
✅ **HTML Emails** - Beautiful responsive emails via SMTP  
✅ **Local/S3 Storage** - Archives all articles  
✅ **REST API** - Manual triggers, webhooks, health checks  
✅ **Free Deployment** - Railway/Render/Fly.io ready  

---

## 🚀 Quick Start (5 minutes)

### 1️⃣ Setup

```bash
cd /Users/luckysolanki/Desktop/dailicle
./setup.sh
```

### 2️⃣ Configure

Edit `.env` with your API keys:
```bash
OPENAI_API_KEY=sk-proj-xxxxx
NOTION_API_KEY=ntn_xxxxx
NOTION_PARENT_PAGE_ID=2bbe80b58b6a8017854ce39c2109eedb
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_TO=your-email@gmail.com
```

### 3️⃣ Run

```bash
source venv/bin/activate
python main.py
```

Server starts at: http://localhost:8000

### 4️⃣ Test

```bash
# Health check
curl http://localhost:8000/api/health

# Send test email
curl -X POST http://localhost:8000/api/test-email

# Generate article
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic_seed": "mental models"}'
```

---

## 📚 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Server health check |
| `/api/generate` | POST | Manual article generation |
| `/api/webhook/generate` | POST | Webhook trigger |
| `/api/test-email` | POST | Test email config |
| `/api/test-services` | POST | Test all services |
| `/api/scheduler/status` | GET | Check next run time |
| `/api/scheduler/trigger` | POST | Force immediate run |
| `/docs` | GET | Interactive API docs |

---

## ☁️ Deployment (Choose One)

### Option 1: Railway.app (Recommended)

**Why:** Easiest, $5/month free credit, auto SSL

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Add environment variables in dashboard.

**Cost:** $5 free/month

---

### Option 2: Render.com

**Why:** Free 750 hours/month (24/7), Git auto-deploy

1. Push to GitHub
2. Connect repo to Render
3. Add environment variables
4. Deploy

**Cost:** Free forever

---

### Option 3: Fly.io

**Why:** 3 free VMs, Docker-based

```bash
brew install flyctl
fly auth login
fly launch
fly secrets set OPENAI_API_KEY=xxx...
fly deploy
```

**Cost:** Free tier (3 VMs)

---

## 💰 Total Monthly Cost

| Service | Cost |
|---------|------|
| **Hosting** | **FREE** (Railway/Render/Fly.io) |
| **OpenAI API** | **$3-5** (gpt-4o-mini, 1 article/day) |
| **Notion API** | **FREE** |
| **Email (Gmail)** | **FREE** |
| **Total** | **~$3-5/month** |

---

## 🔧 Tech Stack

**Why I chose Python + FastAPI:**

- ✅ **Python** - Better for email/SMTP, simpler for this use case
- ✅ **FastAPI** - Modern, async, auto-docs, easy to deploy
- ✅ **APScheduler** - Robust cron scheduling
- ✅ **smtplib** - Built-in email (no extra deps)
- ✅ **Jinja2** - HTML templating
- ✅ **OpenAI SDK** - Official client
- ✅ **Notion SDK** - Official client

**Alternatives I considered:**
- ❌ Node.js - More complex for email/SMTP
- ❌ n8n - Overkill, not needed with custom server

---

## 📋 How It Works

### Daily Workflow (Automatic)

```
6:00 AM IST
    ↓
🤖 Scheduler triggers
    ↓
📝 OpenAI generates article (30-60s)
    ↓
📚 Creates Notion page with formatting
    ↓
📧 Sends beautiful HTML email
    ↓
💾 Saves to local/S3 storage
    ↓
✅ Done! Check your email & Notion
```

### Manual Trigger

```bash
POST /api/generate
{
  "topic_seed": "probabilistic thinking",
  "send_email": true
}
```

Runs same workflow on-demand.

---

## 🛠️ Customization

### Change Schedule

Edit `.env`:
```bash
CRON_SCHEDULE=0 9 * * *  # 9 AM daily
CRON_SCHEDULE=0 6,18 * * *  # 6 AM and 6 PM
CRON_SCHEDULE=0 6 * * 1-5  # Weekdays only
```

### Modify Article Prompt

Edit `prompts/article_prompt.py`:
- Change topic filters
- Adjust length (2000-4000 words default)
- Add/remove sections
- Customize tone

### Email Template

Edit `templates/email_template.html`:
- Change colors
- Add branding
- Modify layout

### OpenAI Model

Edit `.env`:
```bash
OPENAI_MODEL=gpt-4o-mini  # Cheaper, faster
OPENAI_MODEL=gpt-4o       # More powerful
OPENAI_MODEL=gpt-3.5-turbo  # Cheapest
```

---

## 📖 Documentation Files

- **README.md** - Project overview & features
- **QUICKSTART.md** - 5-minute setup guide
- **DEPLOYMENT.md** - Detailed deployment for all platforms
- **.env.example** - Configuration template

---

## 🧪 Testing Checklist

Before deploying, test locally:

```bash
# 1. Start server
python main.py

# 2. Health check
curl http://localhost:8000/api/health

# 3. Test email
curl -X POST http://localhost:8000/api/test-email

# 4. Test services
curl -X POST http://localhost:8000/api/test-services

# 5. Generate test article
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic_seed": "test"}'

# 6. Check scheduler
curl http://localhost:8000/api/scheduler/status
```

All should return success ✅

---

## 🔐 Security Notes

- ✅ Never commit `.env` file
- ✅ Use environment variables on hosting
- ✅ Gmail app password (not main password)
- ✅ HTTPS automatic on all platforms
- ✅ Optional: Add webhook token auth

---

## 🐛 Troubleshooting

### Email not sending?
- Use Gmail **app password** (not regular password)
- Enable 2FA: https://myaccount.google.com/security
- Create app password: https://myaccount.google.com/apppasswords

### Notion error?
- Share page with integration
- Check page ID from URL
- Verify integration has write permission

### OpenAI error?
- Check API key is valid
- Add payment method: https://platform.openai.com/account/billing
- Check rate limits

### Scheduler not running?
- Check logs for errors
- Verify cron syntax is valid
- Ensure timezone is correct

---

## 🎓 Learning Resources

### Master Prompt

The full prompt is in `prompts/article_prompt.py` - it includes:
- Topic selection criteria
- Article structure (12 sections)
- Notion page formatting
- HTML email template instructions
- Citations & references
- Exercises & experiments

This is the **exact prompt** you provided, optimized for OpenAI.

### API Documentation

After starting server, visit:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

Interactive API testing included!

---

## 🚀 Next Steps

### 1. Local Testing (Today)
```bash
./setup.sh
source venv/bin/activate
python main.py
# Test with curl commands above
```

### 2. Deploy (Tomorrow)
```bash
# Choose Railway (recommended)
railway login
railway up
# Add environment variables in dashboard
```

### 3. Monitor (Ongoing)
- Check email at 6 AM IST
- View Notion pages
- Check logs: `railway logs`
- Adjust schedule as needed

---

## 📞 Support

If something doesn't work:

1. **Check logs** - Errors appear in terminal/dashboard
2. **Test services** - `POST /api/test-services`
3. **Verify config** - Double-check `.env` values
4. **Check quotas** - OpenAI billing, rate limits

---

## 🎉 You're All Set!

Your custom server is **better than n8n** because:

- ✅ Simpler (no UI complexity)
- ✅ Cheaper (free hosting + OpenAI only)
- ✅ More control (full code access)
- ✅ Easier to debug (logs & API)
- ✅ Production-ready (proper error handling)

**Total setup time:** 5 minutes  
**Total monthly cost:** ~$3-5  
**Result:** Daily articles in Notion + Email, fully automated

---

**Ready to start?**

```bash
cd /Users/luckysolanki/Desktop/dailicle
./setup.sh
```

Then follow **QUICKSTART.md** for detailed setup.

---

Built with ❤️ using Python, FastAPI, OpenAI, Notion, and SMTP.
