# Dailicle - Setup & Running

## Quick Start

```bash
# 1. Clone and enter directory
cd /Users/luckysolanki/Desktop/dailicle

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Environment Variables

Create a `.env` file with:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Notion
NOTION_API_KEY=ntn_...
NOTION_PARENT_PAGE_ID=your-page-id

# Email (Gmail with App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Daily Mentor
EMAIL_TO=your-email@gmail.com

# MongoDB
MONGODB_URI=mongodb+srv://...

# Optional
TIMEZONE=Asia/Kolkata
```

## Running Locally

```bash
# Activate venv
source venv/bin/activate

# Run article generation
python ./run_daily_article.py
```

## Render Deployment (Cron Job)

1. Push to GitHub
2. Create Render **Cron Job** (not Web Service)
3. Set command: `python ./run_daily_article.py`
4. Set schedule: `0 0 * * *` (daily at midnight UTC = 5:30 AM IST)
5. Add environment variables in Render dashboard

## Project Structure

```
dailicle/
├── run_daily_article.py    # Entry point (Render runs this)
├── config.py               # Environment config
├── requirements.txt        # Dependencies
├── services/
│   ├── llm_service.py          # GPT-5.1 article generation
│   ├── notion_service.py       # Notion page creation
│   ├── email_service.py        # SMTP email sending
│   ├── storage_service.py      # MongoDB article storage
│   ├── topic_history_service.py # Topic tracking for variety
│   └── orchestrator.py         # Workflow coordinator
└── .env                    # Your credentials (not in git)
```
