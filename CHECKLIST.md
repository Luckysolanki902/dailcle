# ✅ Complete Setup Checklist

Use this checklist to ensure everything is configured correctly.

## Pre-requisites

- [ ] Python 3.9 or higher installed
- [ ] OpenAI account with API key
- [ ] Notion account with workspace
- [ ] Gmail account (for SMTP)
- [ ] Terminal/command line access

---

## Setup Steps

### 1. Project Setup

- [ ] Cloned/downloaded project to `/Users/luckysolanki/Desktop/dailicle`
- [ ] Opened terminal in project directory
- [ ] Ran `./start.sh` or `./setup.sh`
- [ ] Virtual environment created (`venv/` directory exists)
- [ ] Dependencies installed (no error messages)

### 2. OpenAI Configuration

- [ ] Created OpenAI account at https://platform.openai.com
- [ ] Added payment method (https://platform.openai.com/account/billing)
- [ ] Generated API key (https://platform.openai.com/api-keys)
- [ ] Copied API key to `.env` as `OPENAI_API_KEY`
- [ ] Verified API key starts with `sk-proj-` or `sk-`
- [ ] Have at least $5 credit available

### 3. Notion Configuration

- [ ] Created Notion account
- [ ] Created or located "Daily articles" page in workspace
- [ ] Created integration at https://www.notion.so/my-integrations
  - [ ] Gave integration a name (e.g., "Dailicle")
  - [ ] Selected correct workspace
  - [ ] Enabled "Read content", "Update content", "Insert content"
- [ ] Copied "Internal Integration Token" to `.env` as `NOTION_API_KEY`
- [ ] Shared "Daily articles" page with integration
  - [ ] Opened page in Notion
  - [ ] Clicked "..." menu → "Add connections"
  - [ ] Selected your integration
- [ ] Copied page ID from URL to `.env` as `NOTION_PARENT_PAGE_ID`
  - URL format: `https://notion.so/workspace/Title-PAGE_ID?...`
  - Page ID is the long hex string after last `/` before `?`

### 4. Email (Gmail) Configuration

- [ ] Have Gmail account
- [ ] Enabled 2-Factor Authentication
  - Visit: https://myaccount.google.com/security
- [ ] Created App Password
  - Visit: https://myaccount.google.com/apppasswords
  - Selected "Mail" and device
  - Copied 16-character password
- [ ] Added to `.env`:
  - [ ] `SMTP_HOST=smtp.gmail.com`
  - [ ] `SMTP_PORT=587`
  - [ ] `SMTP_USER=your-email@gmail.com`
  - [ ] `SMTP_PASSWORD=xxxx xxxx xxxx xxxx` (app password)
  - [ ] `EMAIL_FROM=your-email@gmail.com`
  - [ ] `EMAIL_TO=your-email@gmail.com`

### 5. Schedule Configuration

- [ ] Set timezone in `.env` (e.g., `TIMEZONE=Asia/Kolkata`)
- [ ] Set cron schedule in `.env` (e.g., `CRON_SCHEDULE=0 6 * * *`)
- [ ] Verified cron format is correct (5 parts: minute hour day month day_of_week)

### 6. Optional: Cloud Storage (S3)

If you want to backup articles to S3:
- [ ] Created AWS account
- [ ] Created S3 bucket
- [ ] Generated access keys (IAM)
- [ ] Added to `.env`:
  - [ ] `AWS_ACCESS_KEY_ID=your-key`
  - [ ] `AWS_SECRET_ACCESS_KEY=your-secret`
  - [ ] `S3_BUCKET_NAME=your-bucket`

If not using S3:
- [ ] Left S3 settings commented out (articles save locally)

---

## Testing

### Local Testing

- [ ] Activated virtual environment: `source venv/bin/activate`
- [ ] Ran configuration test: `python test_setup.py`
  - [ ] Scheduler config: ✅ PASS
  - [ ] Notion config: ✅ PASS
  - [ ] Email test: ✅ PASS
  - [ ] OpenAI test: ✅ PASS (or skipped)

### Server Testing

- [ ] Started server: `python main.py`
- [ ] Server started without errors
- [ ] Opened http://localhost:8000 in browser
- [ ] Saw welcome page with endpoints

### API Testing

In another terminal:

- [ ] Health check: `curl http://localhost:8000/api/health`
  - [ ] Got `"status": "healthy"`
  - [ ] Got `"scheduler_running": true`
  - [ ] Got next run time

- [ ] Scheduler status: `curl http://localhost:8000/api/scheduler/status`
  - [ ] Verified next run time is correct
  - [ ] Verified cron schedule matches `.env`

- [ ] Test email: `curl -X POST http://localhost:8000/api/test-email`
  - [ ] Got success response
  - [ ] Received email in inbox
  - [ ] Email renders correctly (HTML)

- [ ] View API docs: Opened http://localhost:8000/docs
  - [ ] Swagger UI loaded
  - [ ] All endpoints visible

### Article Generation Test

**Warning: This uses OpenAI credits (~$0.10-0.15)**

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic_seed": "test topic", "send_email": true}'
```

- [ ] Request accepted (200 OK)
- [ ] Wait 30-60 seconds for generation
- [ ] Got success response with:
  - [ ] `"status": "success"`
  - [ ] `"topic_title": "..."`
  - [ ] `"notion_url": "https://notion.so/..."`
  - [ ] `"email_sent": true`

- [ ] Checked Notion workspace
  - [ ] New page created under "Daily articles"
  - [ ] Page has proper formatting
  - [ ] Properties filled (tags, difficulty, etc.)
  - [ ] Content is readable

- [ ] Checked email inbox
  - [ ] Received article email
  - [ ] Subject line correct
  - [ ] HTML renders beautifully
  - [ ] All sections present
  - [ ] Links work
  - [ ] Notion link at bottom works

- [ ] Checked local storage
  - [ ] `articles/` directory has files
  - [ ] JSON file created
  - [ ] HTML file created

---

## Deployment Preparation

### Pre-deployment Checks

- [ ] All local tests passed
- [ ] `.env` file contains all required values
- [ ] `.env` is in `.gitignore` (never commit secrets!)
- [ ] Chose deployment platform:
  - [ ] Railway.app (recommended - easiest)
  - [ ] Render.com (free 750 hrs/mo)
  - [ ] Fly.io (3 free VMs)

### Railway.app Deployment

- [ ] Installed Railway CLI: `npm install -g @railway/cli`
- [ ] Logged in: `railway login`
- [ ] Initialized project: `railway init`
- [ ] Added environment variables in dashboard:
  - [ ] OPENAI_API_KEY
  - [ ] NOTION_API_KEY
  - [ ] NOTION_PARENT_PAGE_ID
  - [ ] SMTP_HOST
  - [ ] SMTP_PORT
  - [ ] SMTP_USER
  - [ ] SMTP_PASSWORD
  - [ ] EMAIL_FROM
  - [ ] EMAIL_FROM_NAME
  - [ ] EMAIL_TO
  - [ ] TIMEZONE
  - [ ] CRON_SCHEDULE
- [ ] Deployed: `railway up`
- [ ] Got deployment URL
- [ ] Tested deployed API:
  - [ ] `curl https://your-app.railway.app/api/health`
  - [ ] Status is healthy

### Render.com Deployment

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Signed up at https://render.com
- [ ] Created new Web Service
- [ ] Connected GitHub repository
- [ ] Added all environment variables in dashboard
- [ ] Deployed automatically
- [ ] Got deployment URL
- [ ] Tested deployed API

### Fly.io Deployment

- [ ] Installed Fly CLI: `brew install flyctl`
- [ ] Logged in: `fly auth login`
- [ ] Launched app: `fly launch`
- [ ] Set all secrets: `fly secrets set KEY=value`
- [ ] Deployed: `fly deploy`
- [ ] Got deployment URL
- [ ] Tested deployed API

---

## Post-Deployment Verification

### Production Tests

- [ ] Health check: `curl https://your-app.com/api/health`
- [ ] Scheduler running in production
- [ ] Next run time is correct (check timezone)
- [ ] Test email in production
- [ ] Generate test article in production
- [ ] Check Notion page created from production
- [ ] Check email received from production

### Monitoring Setup

- [ ] Know how to view logs:
  - Railway: `railway logs`
  - Render: Dashboard → Logs
  - Fly.io: `fly logs`
- [ ] Set up log alerts (optional)
- [ ] Bookmarked dashboard URL
- [ ] Saved deployment URL
- [ ] Noted where environment variables are managed

---

## Daily Operation

### Automated (No Action Needed)

- [ ] Scheduler runs automatically at configured time
- [ ] Article generated daily
- [ ] Notion page created daily
- [ ] Email sent daily

### Manual Monitoring

Daily:
- [ ] Check email for new article
- [ ] Verify Notion page created
- [ ] Glance at topics to ensure quality

Weekly:
- [ ] Check OpenAI usage/costs
- [ ] Review logs for any errors
- [ ] Verify all articles are good quality

Monthly:
- [ ] Check OpenAI bill (~$3-5 expected)
- [ ] Review all articles generated
- [ ] Adjust prompt if needed
- [ ] Consider schedule changes

---

## Troubleshooting Checklist

If something goes wrong, check:

### Email Not Received

- [ ] Check spam folder
- [ ] Verify SMTP credentials in `.env`
- [ ] Test with: `curl -X POST https://your-app.com/api/test-email`
- [ ] Confirm using app password (not regular password)
- [ ] Check Gmail account hasn't blocked access

### Notion Page Not Created

- [ ] Verify integration is shared with page
- [ ] Check page ID in `.env` is correct
- [ ] Confirm integration has write permissions
- [ ] Test Notion API key is valid
- [ ] Check logs for specific error

### Scheduler Not Running

- [ ] Verify server is running (check logs)
- [ ] Check cron format in `.env` (5 parts)
- [ ] Verify timezone is correct
- [ ] Check next run time: `curl .../api/scheduler/status`
- [ ] Restart server if needed

### OpenAI Errors

- [ ] Check API key is valid
- [ ] Verify payment method is added
- [ ] Check credit balance
- [ ] Review rate limits
- [ ] Try different model in `.env`

### General Debugging

- [ ] Check logs first (most errors explained)
- [ ] Run `python test_setup.py` locally
- [ ] Test individual services with `/api/test-services`
- [ ] Verify environment variables are set
- [ ] Try restarting server
- [ ] Check OpenAI status page
- [ ] Check Notion API status

---

## Success Criteria

You're fully set up when:

✅ Server runs without errors  
✅ Scheduler shows next run time  
✅ Test email arrives in inbox  
✅ Test article generates successfully  
✅ Notion page created with formatting  
✅ Email received with beautiful HTML  
✅ Local/cloud storage working  
✅ Deployed to production  
✅ Production health check passes  
✅ First automated article generated overnight  

---

## Cost Tracking

Keep track of expenses:

### Monthly Costs

| Service | Expected Cost | Actual Cost |
|---------|---------------|-------------|
| Railway/Render/Fly.io | FREE | $ |
| OpenAI API (30 articles) | $3-5 | $ |
| Notion API | FREE | $ |
| Email (Gmail) | FREE | $ |
| S3 (optional) | $0-1 | $ |
| **Total** | **$3-5** | **$** |

### Usage Tracking

- [ ] OpenAI dashboard bookmarked: https://platform.openai.com/usage
- [ ] Check weekly for unexpected usage
- [ ] Set up billing alerts if available
- [ ] Monitor article count vs cost

---

## Next Steps After Setup

Once everything is working:

### Immediate (Week 1)
- [ ] Let it run for a week
- [ ] Read all generated articles
- [ ] Check quality and relevance
- [ ] Note any improvements needed

### Short-term (Month 1)
- [ ] Adjust topic filters if needed (edit `prompts/article_prompt.py`)
- [ ] Customize email template colors/branding
- [ ] Fine-tune schedule if needed
- [ ] Consider adding more recipients

### Long-term
- [ ] Archive best articles
- [ ] Share with team/friends (if desired)
- [ ] Add custom features (see customization docs)
- [ ] Optimize OpenAI model/costs
- [ ] Build article collection in Notion

---

## Documentation Reference

For detailed information, see:

- **README.md** - Project overview and features
- **QUICKSTART.md** - Step-by-step setup guide
- **DEPLOYMENT.md** - Detailed deployment instructions
- **PROJECT_SUMMARY.md** - Complete system architecture
- **ARCHITECTURE.txt** - Visual system overview

---

## Support Resources

If you need help:

1. **Check logs** - Most errors are self-explanatory
2. **Test services** - `POST /api/test-services`
3. **Review docs** - All questions likely answered
4. **Check API status pages**:
   - OpenAI: https://status.openai.com
   - Notion: https://status.notion.so
5. **Verify configuration** - Double-check `.env` values

---

**Last Updated:** December 1, 2025

**Version:** 1.0.0

**Setup Time:** ~5-10 minutes

**Status:** 
- [ ] Not started
- [ ] In progress
- [ ] Testing
- [ ] Deployed
- [ ] Production ready ✅
