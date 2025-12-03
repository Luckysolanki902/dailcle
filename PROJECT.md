# Dailicle

**A personal AI-powered daily article system that generates deeply researched, eloquent longform essays tailored to my life as a founder, engineer, and human being.**

---

## What It Does

Every day at 5:30 AM IST, Dailicle automatically:

1. **Generates a 4,000–6,000 word essay** using GPT-5.1 with web search
2. **Creates a Notion page** with the full article
3. **Sends an email** with the article to my inbox
4. **Tracks topic history** in MongoDB to ensure variety

---

## Why I Built This

I wanted a personal mentor that sends me one thoughtful, well-researched article every morning — not generic self-help, but deeply practical essays that match my actual life:

- **Founder/CTO struggles**: ego management, shipping consistently, validating ideas, A/B testing, customer thinking
- **Personal growth**: spotlight effect, showing off, being judged, staying grounded as success comes
- **Relationships**: difficult family conversations, consoling someone, text message scripts, caste/identity discussions
- **Systems thinking**: feedback loops, cognitive biases, habit engineering, decision-making under uncertainty

The articles are written in an essayist style — narrative, research-backed, with micro-experiments I can actually try that week.

---

## How It Works

```
Render Cron Job (daily)
        │
        ▼
run_daily_article.py
        │
        ├── topic_history_service.py  →  MongoDB (avoid past topics)
        │
        ├── llm_service.py            →  GPT-5.1 + web search
        │
        ├── notion_service.py         →  Create Notion page
        │
        ├── email_service.py          →  Send to my inbox
        │
        └── storage_service.py        →  Save full article to MongoDB
```

---

## The Prompt

The magic is in the prompt. It's a detailed instruction that tells GPT-5.1 to:

- Write like a thinker who also ships products
- Use vivid examples, short human stories, precise analogies
- Include 3+ micro-experiments with step-by-step instructions
- Explain 4–8 psychological concepts with definitions and implications
- Provide text-message scripts and consoling templates
- Offer A/B test blueprints for product ideas
- End with a 30/90/365 day roadmap

Topics are diverse: systems thinking, ego, design aesthetics (why does a Porsche 911 look right?), habit engineering, startup validation, family conversations, and more.

---

## Tech Stack

- **Python 3.11+**
- **OpenAI GPT-5.1** (Responses API with web search)
- **MongoDB** (topic history + full article storage)
- **Notion API** (article pages)
- **Gmail SMTP** (email delivery)
- **Render Cron Job** (daily scheduling)

---

## MongoDB Collections

- `topic_history` — lightweight metadata (title, category, tags, date, notion_url)
- `articles` — full article content (markdown, HTML, youtube, papers, etc.)

Both are linked via `topic_history_id` for querying.

---

## Personal Note

This isn't a product for others — it's a tool I built for myself. Every morning I wake up to an essay that feels like it was written by a mentor who knows my exact situation: the ego creeping in with success, the fear of being judged, the struggle to finish side projects, the tension with family about caste and tradition.

It's like having a personal essayist who reads psychology papers, watches my favorite YouTube channels, and writes specifically for me.

---

*Built by Lucky Solanki, December 2025*
