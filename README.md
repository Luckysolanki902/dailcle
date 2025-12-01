# Dailicle - AI-Powered Daily Article Generator

Automated daily article generation system that researches topics, writes mentor-style articles, creates Notion pages, and sends beautiful HTML emails.

## Features

- 🤖 **AI Research & Writing**: Uses OpenAI to generate high-quality, research-backed articles
- 📚 **Notion Integration**: Automatically creates formatted subpages in your Notion workspace
- 📧 **Email Delivery**: Sends beautifully formatted HTML emails with inline CSS
- ⏰ **Scheduled Generation**: Runs daily via cron (default: 6:00 AM IST)
- 🔄 **Manual Triggers**: Webhook and API endpoints for on-demand generation
- 🎯 **Curated Topics**: Focuses on founder/CTO-relevant psychology, leadership, product, and tech topics

## Architecture

```
dailicle/
├── services/
│   ├── llm_service.py       # OpenAI article generation
│   ├── notion_service.py    # Notion API integration
│   ├── email_service.py     # SMTP email sender
│   └── storage_service.py   # Optional S3/cloud storage
├── prompts/
│   └── article_prompt.py    # Master LLM prompt
├── templates/
│   └── email_template.html  # Email HTML template
├── api/
│   └── routes.py            # FastAPI endpoints
├── scheduler.py             # Cron job scheduler
├── config.py                # Configuration management
├── main.py                  # FastAPI application
└── requirements.txt         # Dependencies
```

## Quick Start

### 🚀 Instant Setup (Recommended)

```bash
cd /Users/luckysolanki/Desktop/dailicle
./start.sh
```

This interactive script will guide you through the entire setup process!

### Manual Setup

```bash
cd /Users/luckysolanki/Desktop/dailicle
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

**Required credentials:**
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Notion integration token (create at https://www.notion.so/my-integrations)
- Gmail app password (https://myaccount.google.com/apppasswords)

### 3. Set Up Notion

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Share your "Daily articles" page with the integration
3. Copy the page ID from the URL (the part after the last `/` and before `?`)

### 4. Run the Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

## API Endpoints

### Generate Article (Manual Trigger)

```bash
POST /api/generate
Content-Type: application/json

{
  "topic_seed": "probabilistic thinking",  # Optional
  "send_email": true                        # Optional, default: true
}

Response:
{
  "status": "success",
  "topic_title": "How to Think Probabilistically",
  "notion_url": "https://notion.so/...",
  "email_sent": true,
  "timestamp": "2025-12-01T06:00:00+05:30"
}
```

### Health Check

```bash
GET /health

Response:
{
  "status": "healthy",
  "scheduler_running": true,
  "next_run": "2025-12-02T06:00:00+05:30"
}
```

### Webhook Trigger

```bash
POST /webhook/generate?token=your-secret-token
```

## Deployment

### Option 1: Railway.app (Recommended - Free $5/month credit)

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Add environment variables in Railway dashboard
4. Your app will be live at `https://your-app.railway.app`

**Cost**: Free tier includes $5 credit/month (enough for ~150 API calls)

### Option 2: Render.com (Free tier available)

1. Create a `render.yaml`:
```yaml
services:
  - type: web
    name: dailicle
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

2. Connect your GitHub repo to Render
3. Deploy automatically on push

**Cost**: Free tier with 750 hours/month (enough for 24/7 operation)

### Option 3: Fly.io (Generous free tier)

```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

**Cost**: Free tier includes 3 shared VMs

## Cost Estimation (Monthly)

**For personal use (1 article/day):**
- OpenAI API (gpt-4o-mini): ~$3-5/month
- Notion API: Free
- Email (SMTP): Free
- Hosting: Free (Railway/Render/Fly.io)

**Total: ~$3-5/month**

## Customization

### Change Schedule

Edit `.env`:
```bash
CRON_SCHEDULE="0 6 * * *"  # Format: minute hour day month day_of_week
# Examples:
# "0 9 * * *"    - Daily at 9 AM
# "0 6,18 * * *" - Twice daily at 6 AM and 6 PM
# "0 6 * * 1-5"  - Weekdays only at 6 AM
```

### Modify Article Prompt

Edit `prompts/article_prompt.py` to:
- Change topic filters
- Adjust article length
- Modify tone and style
- Add/remove sections

### Custom Email Template

Edit `templates/email_template.html` for branding, colors, and layout.

## Monitoring

View logs:
```bash
# Railway
railway logs

# Render
# Check logs in dashboard

# Fly.io
fly logs
```

## Troubleshooting

### "SMTP Authentication Error"
- Use Gmail app password, not your regular password
- Enable 2FA and create app password at https://myaccount.google.com/apppasswords

### "Notion API Error: object not found"
- Ensure integration is shared with the parent page
- Check page ID is correct (from URL)

### "OpenAI Rate Limit"
- Add delay between retries
- Use gpt-4o-mini instead of gpt-4o for lower costs

### "Scheduler not running"
- Check timezone in `.env` matches your location
- Verify cron expression is valid

## Development

Run tests:
```bash
pytest tests/ -v
```

Format code:
```bash
black .
```

Type check:
```bash
mypy .
```

## Security

- Never commit `.env` file
- Use app passwords for Gmail (not main password)
- Rotate API keys regularly
- Use environment variables on hosting platform
- Enable rate limiting in production

## License

MIT

## Support

For issues or questions, check the logs or create an issue in the repository.

---

**Built with**: FastAPI, OpenAI Agents SDK, Notion API, Python stdlib
