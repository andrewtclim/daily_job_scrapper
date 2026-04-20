# Daily Job Scraper

Scrapes Stripe and Airbnb job boards for **Data Scientist** postings and emails you when new ones appear.

Runs automatically 4x a day via GitHub Actions.

## How it works

1. Fetches job listings from each company's Greenhouse board
2. Compares against previously seen jobs (`seen_jobs.json`)
3. Emails you any new matches
4. Commits the updated state back to the repo

## Setup

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `EMAIL_SENDER` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password ([generate one here](https://myaccount.google.com/apppasswords)) |
| `EMAIL_RECIPIENT` | Address to receive alerts |

### 2. Push to GitHub

```bash
git add .
git commit -m "feat: add daily job scraper"
git push -u origin main
```

The workflow starts running on schedule immediately after push.

### 3. Trigger a manual test run

**Actions tab → Job Scraper → Run workflow**

## Customization

| What | Where |
|---|---|
| Add/change companies | `COMPANIES` dict in `scraper.py` (use the Greenhouse board slug) |
| Change job title filter | `TITLE_KEYWORDS` list in `scraper.py` |
| Change schedule | `cron` expression in `.github/workflows/scrape.yml` |

## Schedule

Runs at **00:00, 06:00, 12:00, 18:00 UTC** daily.
