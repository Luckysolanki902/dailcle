# Quick Start Guide

Get your Dailicle server running in 5 minutes.

## Prerequisites

- Python 3.9+ installed
- OpenAI API key (https://platform.openai.com/api-keys)
- Notion account with integration (https://www.notion.so/my-integrations)
- Gmail account with app password (https://myaccount.google.com/apppasswords)

## Installation

### Option 1: Automatic Setup (Recommended)

```bash
cd /Users/luckysolanki/Desktop/dailicle
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file from template
- Set up directories

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
```

## Configuration

Edit `.env` file with your credentials:

```bash
nano .env
# or
code .env
```

### Required Settings:

**OpenAI:**
```
OPENAI_API_KEY=sk-proj-xxxxx...
```
Get from: https://platform.openai.com/api-keys

**Notion:**
```
NOTION_API_KEY=ntn_xxxxx...
NOTION_PARENT_PAGE_ID=2bbe80b58b6a8017854ce39c2109eedb
```
Setup:
1. Create integration: https://www.notion.so/my-integrations
2. Click "New integration" → Give it a name
3. Copy the "Internal Integration Token"
4. Share your "Daily articles" page with the integration
5. Get page ID from URL (the long string after `/` before `?`)

**Email (Gmail):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App password, not regular password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Lucky's Daily Mentor
EMAIL_TO=your-email@gmail.com
```

Gmail app password setup:
1. Enable 2FA: https://myaccount.google.com/security
2. Create app password: https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Copy the 16-character password

**Schedule:**
```
TIMEZONE=Asia/Kolkata
CRON_SCHEDULE=0 6 * * *  # Daily at 6:00 AM
```

Cron format: `minute hour day month day_of_week`
Examples:
- `0 6 * * *` - Every day at 6 AM
- `0 6,18 * * *` - Twice daily at 6 AM and 6 PM
- `0 6 * * 1-5` - Weekdays only at 6 AM
- `0 */6 * * *` - Every 6 hours

## Running Locally

### Start the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

Server starts at: http://localhost:8000

### View API Docs

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "scheduler_running": true,
  "next_run": "2025-12-02T06:00:00+05:30",
  "timezone": "Asia/Kolkata"
}
```

### 2. Test Email

```bash
curl -X POST http://localhost:8000/api/test-email
```

Check your inbox for test email.

### 3. Test All Services

```bash
curl -X POST http://localhost:8000/api/test-services
```

This tests OpenAI, Email, and configurations.

### 4. Generate Test Article

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic_seed": "decision making under uncertainty",
    "send_email": true,
    "save_to_storage": true
  }'
```

This will:
1. Generate article using OpenAI (~30-60 seconds)
2. Create Notion page
3. Send HTML email
4. Save to local storage

### 5. Check Scheduler

```bash
curl http://localhost:8000/api/scheduler/status
```

### 6. Manual Trigger

```bash
curl -X POST http://localhost:8000/api/scheduler/trigger
```

## API Endpoints

### Generate Article (Manual)

```bash
POST /api/generate
Content-Type: application/json

{
  "topic_seed": "optional topic hint",
  "send_email": true,
  "save_to_storage": true
}
```

### Webhook (for automation)

```bash
POST /api/webhook/generate?topic_seed=cognitive+biases
```

Use this with:
- IFTTT
- Zapier
- GitHub Actions
- Shortcuts (iOS)

### Health & Status

```bash
GET /api/health                 # Simple health check
GET /api/scheduler/status       # Scheduler details
POST /api/scheduler/trigger     # Manual trigger
POST /api/test-email           # Send test email
POST /api/test-services        # Test all services
```

## Scheduler Behavior

The scheduler runs automatically based on your `CRON_SCHEDULE`:

- **Default:** Daily at 6:00 AM IST
- **Automatic:** No manual intervention needed
- **Persistent:** Survives server restarts
- **Timezone-aware:** Uses `TIMEZONE` setting

### View Next Run:

```bash
curl http://localhost:8000/api/scheduler/status
```

### Change Schedule:

Edit `.env`:
```bash
CRON_SCHEDULE=0 9 * * *  # Change to 9 AM
```

Restart server:
```bash
# Press Ctrl+C, then restart
python main.py
```

## File Structure

```
dailicle/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration management
├── scheduler.py            # Cron scheduler
├── requirements.txt        # Python dependencies
├── .env                    # Your credentials (DO NOT COMMIT)
│
├── api/
│   └── routes.py          # API endpoints
│
├── services/
│   ├── llm_service.py     # OpenAI article generation
│   ├── notion_service.py  # Notion API integration
│   ├── email_service.py   # SMTP email sender
│   ├── orchestrator.py    # Workflow coordinator
│   └── storage_service.py # Local/S3 storage
│
├── prompts/
│   └── article_prompt.py  # Master LLM prompt
│
├── templates/
│   └── email_template.html # Email HTML template
│
└── articles/              # Local storage (auto-created)
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### "SMTP Authentication Error"
- Use Gmail **app password**, not regular password
- Enable 2FA first
- Create app password at https://myaccount.google.com/apppasswords

### "Notion API Error: object not found"
- Share your Notion page with the integration
- Check page ID in URL is correct
- Ensure integration has write permissions

### "OpenAI API Error"
- Check API key is valid
- Ensure you have credits: https://platform.openai.com/account/billing
- Try a different model: `OPENAI_MODEL=gpt-3.5-turbo` in `.env`

### "Scheduler not running"
- Check logs for errors
- Verify cron format is valid
- Ensure timezone is correct

### "Article takes too long"
- Normal: 30-60 seconds for generation
- Timeout: Increase `max_tokens` in config
- Alternative: Use smaller model (gpt-3.5-turbo)

## Deployment

Ready to deploy? See **DEPLOYMENT.md** for:
- Railway.app (recommended)
- Render.com
- Fly.io

**Cost:** ~$3-5/month (just OpenAI API, hosting is free)

## Next Steps

1. ✅ Test locally with `curl` commands above
2. ✅ Verify email arrives correctly
3. ✅ Check Notion page is created
4. ✅ Let scheduler run overnight
5. 🚀 Deploy to Railway/Render (see DEPLOYMENT.md)

## Customization

### Change Article Length

Edit `config.py`:
```python
max_tokens: int = 16000  # Increase for longer articles
```

### Modify Prompt

Edit `prompts/article_prompt.py` to:
- Change topic filters
- Adjust tone and style
- Add/remove sections
- Customize for your needs

### Email Template

Edit `templates/email_template.html` for:
- Different colors
- Custom branding
- Layout changes

## Support

Check logs for errors:
```bash
# Logs appear in terminal when running locally
# On deployment, use platform-specific log viewers
```

Test individual components:
```bash
curl -X POST http://localhost:8000/api/test-services
```

---

**You're all set! 🎉**

Run `python main.py` and let it generate your first article.
