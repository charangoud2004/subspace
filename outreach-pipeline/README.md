# Automated B2B Cold Outreach Pipeline

Python CLI that takes one seed company domain, finds lookalike companies, finds senior decision makers, resolves work emails, shows a mandatory safety checkpoint, and sends personalized email through Brevo only after explicit confirmation.

## Setup

```bash
cd outreach-pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

If PowerShell blocks activation, run this once for your current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If `python -m venv .venv` was interrupted, delete the partial `.venv` folder and create it again before activating.

Fill `.env` with your API keys:

- `OCEAN_API_KEY`: Ocean.io dashboard, Settings, API Tokens.
- `PROSPEO_API_KEY`: Prospeo API Management dashboard.
- `BREVO_API_KEY`: Brevo SMTP/API settings.
- `SENDER_EMAIL` and `SENDER_NAME`: a sender registered and verified in Brevo.
- `HUNTER_API_KEY`: Hunter.io email finder API key.

## Run

```bash
python pipeline.py stripe.com
```

Or run without an argument:

```bash
python pipeline.py
```

## Pipeline Stages

1. Ocean.io finds 10-15 lookalike company domains and writes `stage1_domains.json`.
2. Prospeo searches up to 10 domains for C-suite, VP, director, founder, and president-level contacts with LinkedIn URLs, then writes `stage2_contacts.json`.
3. Hunter.io resolves work emails from each contact's name and domain, then writes `stage3_leads.json`.
4. Brevo sends the personalized email after the console checkpoint receives exactly `y`. Sent messages are appended to `sent_emails.json`.

Errors are appended to `errors.log` with timestamps and stage names.

## Current API Notes

- Ocean.io public docs currently show v3 search endpoints under `https://api.ocean.io`, with API token auth through `x-api-token`. If your account expects Bearer auth instead, set `OCEAN_AUTH_HEADER=Authorization`.
- Prospeo's current public docs use `POST /search-person` with `X-KEY` auth. The older `/domain-search` shape from the prompt is still supported by configuration: set `PROSPEO_ENDPOINT=/domain-search`.
- Hunter.io email resolution uses `GET /email-finder` with the contact's domain, first name, and last name.
- Brevo sending uses `POST /smtp/email` with the `api-key` header.

## Limits

- Ocean.io: credits are limited, so the script performs one lookalike search and caps output at 15.
- Prospeo free tier: 50 requests/day, 1 request/second. The script caps at 10 domains and sleeps 1.1 seconds between calls.
- Hunter.io: 25 searches/month on the free tier.
- Brevo: 300 emails/day on common free-tier limits. The script sleeps 0.5 seconds between sends.

## Safety

The script always prints a summary before sending:

```text
Proceed? (y/n):
```

Only an exact `y` sends email. Any other input exits with `Aborted. No emails sent.`
