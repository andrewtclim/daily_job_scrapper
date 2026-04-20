"""
Job scraper for Stripe and Airbnb via Greenhouse public API.
Tracks seen jobs in seen_jobs.json and emails new postings.
"""

import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

COMPANIES = {
    "Stripe": "stripe",
    "Airbnb": "airbnb",
}

TITLE_KEYWORDS = ["data scientist"]  # case-insensitive

STATE_FILE = Path(__file__).parent / "seen_jobs.json"

# ── Greenhouse API ─────────────────────────────────────────────────────────────

def fetch_jobs(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json().get("jobs", [])


def matches_title(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in TITLE_KEYWORDS)


# ── State ──────────────────────────────────────────────────────────────────────

def load_seen() -> set[str]:
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        return set(data)
    return set()


def save_seen(seen: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen), indent=2))


# ── Email ──────────────────────────────────────────────────────────────────────

def send_email(new_jobs: list[dict]) -> None:
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    subject = f"[Job Alert] {len(new_jobs)} new posting(s) found"

    lines = []
    for job in new_jobs:
        lines.append(f"🏢 {job['company']}")
        lines.append(f"   Title : {job['title']}")
        lines.append(f"   Location: {job.get('location', 'N/A')}")
        lines.append(f"   Link  : {job['url']}")
        lines.append("")

    body = "\n".join(lines)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent: {subject}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    seen = load_seen()
    new_jobs: list[dict] = []

    for company_name, board_token in COMPANIES.items():
        print(f"Fetching jobs for {company_name}...")
        try:
            jobs = fetch_jobs(board_token)
        except requests.RequestException as e:
            print(f"  ERROR fetching {company_name}: {e}")
            continue

        matched = [j for j in jobs if matches_title(j.get("title", ""))]
        print(f"  Found {len(matched)} matching job(s) out of {len(jobs)} total")

        for job in matched:
            job_id = str(job["id"])
            if job_id not in seen:
                seen.add(job_id)
                new_jobs.append(
                    {
                        "company": company_name,
                        "title": job["title"],
                        "location": job.get("location", {}).get("name", "N/A"),
                        "url": job.get("absolute_url", ""),
                    }
                )

    save_seen(seen)
    print(f"\n{len(new_jobs)} new job(s) found across all companies.")

    if new_jobs:
        send_email(new_jobs)
    else:
        print("No new jobs — no email sent.")


if __name__ == "__main__":
    main()
