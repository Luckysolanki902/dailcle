# Deployment Guide

Choose one of these free hosting options for your Dailicle server.

## Option 1: Railway.app (Recommended)

**Why Railway:** Easiest setup, $5/month free credit, automatic SSL, great for Python apps.

### Steps:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```

2. **Login and Initialize:**
   ```bash
   railway login
   cd /Users/luckysolanki/Desktop/dailicle
   railway init
   ```

3. **Set Environment Variables:**
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key
   railway variables set NOTION_API_KEY=ntn-your-key
   railway variables set NOTION_PARENT_PAGE_ID=your-page-id
   railway variables set SMTP_HOST=smtp.gmail.com
   railway variables set SMTP_PORT=587
   railway variables set SMTP_USER=your-email@gmail.com
   railway variables set SMTP_PASSWORD=your-app-password
   railway variables set EMAIL_FROM=your-email@gmail.com
   railway variables set EMAIL_FROM_NAME="Lucky's Daily Mentor"
   railway variables set EMAIL_TO=lucky@example.com
   railway variables set TIMEZONE=Asia/Kolkata
   railway variables set CRON_SCHEDULE="0 6 * * *"
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Get URL:**
   ```bash
   railway domain
   ```

Your app will be live at `https://your-app.railway.app`

**Cost:** $5 free credit/month (enough for ~150 OpenAI API calls)

---

## Option 2: Render.com

**Why Render:** Generous free tier, 750 hours/month, auto-deploy from Git.

### Steps:

1. **Push to GitHub:**
   ```bash
   cd /Users/luckysolanki/Desktop/dailicle
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/dailicle.git
   git push -u origin main
   ```

2. **Create Render Account:**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect Python and `render.yaml`

4. **Add Environment Variables:**
   In Render dashboard, go to "Environment" and add:
   - `OPENAI_API_KEY`
   - `NOTION_API_KEY`
   - `NOTION_PARENT_PAGE_ID`
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `EMAIL_FROM`
   - `EMAIL_FROM_NAME`
   - `EMAIL_TO`
   - `TIMEZONE`
   - `CRON_SCHEDULE`

5. **Deploy:**
   Click "Create Web Service"

**Cost:** Free tier (750 hours/month = 24/7 operation)

---

## Option 3: Fly.io

**Why Fly.io:** 3 free shared VMs, good for personal projects.

### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   # or
   brew install flyctl
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Launch App:**
   ```bash
   cd /Users/luckysolanki/Desktop/dailicle
   fly launch
   # Follow prompts, say yes to creating app
   ```

4. **Set Secrets:**
   ```bash
   fly secrets set OPENAI_API_KEY=sk-your-key
   fly secrets set NOTION_API_KEY=ntn-your-key
   fly secrets set NOTION_PARENT_PAGE_ID=your-page-id
   fly secrets set SMTP_HOST=smtp.gmail.com
   fly secrets set SMTP_PORT=587
   fly secrets set SMTP_USER=your-email@gmail.com
   fly secrets set SMTP_PASSWORD=your-app-password
   fly secrets set EMAIL_FROM=your-email@gmail.com
   fly secrets set EMAIL_FROM_NAME="Lucky's Daily Mentor"
   fly secrets set EMAIL_TO=lucky@example.com
   fly secrets set TIMEZONE=Asia/Kolkata
   fly secrets set CRON_SCHEDULE="0 6 * * *"
   ```

5. **Deploy:**
   ```bash
   fly deploy
   ```

**Cost:** Free tier (3 shared VMs)

---

## Cost Comparison (Monthly)

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Railway | $5 credit | ~150 API calls |
| Render | 750 hours | Enough for 24/7 |
| Fly.io | 3 shared VMs | Good for personal use |
| **OpenAI** | Pay-as-you-go | ~$3-5/month (gpt-4o-mini) |
| **Notion** | Free | Unlimited API calls |
| **Email** | Free | Gmail SMTP |

**Total estimated cost:** $3-5/month (just OpenAI)

---

## After Deployment

### 1. Test the API

```bash
# Check health
curl https://your-app.railway.app/api/health

# Send test email
curl -X POST https://your-app.railway.app/api/test-email

# Test all services
curl -X POST https://your-app.railway.app/api/test-services
```

### 2. Manual Generation

```bash
# Generate article with topic seed
curl -X POST https://your-app.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic_seed": "probabilistic thinking"}'
```

### 3. View Logs

```bash
# Railway
railway logs

# Render
# Check dashboard → Logs tab

# Fly.io
fly logs
```

### 4. Check Scheduler

```bash
curl https://your-app.railway.app/api/scheduler/status
```

---

## Troubleshooting

### "SMTP Authentication Error"
- Use Gmail app password (not regular password)
- Enable 2FA on Google account
- Create app password at https://myaccount.google.com/apppasswords

### "Notion API Error"
- Share your Notion page with the integration
- Check page ID is correct (from URL)
- Verify integration has write permissions

### "OpenAI Rate Limit"
- Upgrade to paid OpenAI account
- Add payment method at https://platform.openai.com/account/billing

### "Scheduler Not Running"
- Check logs for errors
- Verify timezone is correct
- Validate cron expression

---

## Monitoring

### View Next Run Time

```bash
curl https://your-app.railway.app/api/scheduler/status
```

### Manual Trigger

```bash
curl -X POST https://your-app.railway.app/api/scheduler/trigger
```

### Webhook (for IFTTT/Zapier)

```bash
curl -X POST "https://your-app.railway.app/api/webhook/generate?topic_seed=mental+models"
```

---

## Scaling

For higher usage:
1. **Upgrade hosting plan** (Railway Pro: $20/month unlimited)
2. **Add rate limiting** to prevent abuse
3. **Use Redis** for session management
4. **Add monitoring** (Sentry, DataDog)
5. **Implement queue** (Celery, RQ) for background tasks

---

## Security Checklist

- ✅ Never commit `.env` file
- ✅ Use environment variables on hosting platform
- ✅ Rotate API keys regularly
- ✅ Enable HTTPS (automatic on all platforms)
- ✅ Add webhook authentication token (optional)
- ✅ Monitor usage and costs

---

## Support

For issues:
1. Check logs first
2. Test individual services with `/api/test-services`
3. Verify environment variables
4. Check API quotas and limits
