# Outreach Pipeline Walkthrough

This file explains how the automated B2B cold outreach pipeline works from setup to final email sending. It is meant to be the plain-English tour you can use before a demo, during handoff, or when debugging an API issue.

## What This Project Does

The application is a Python command-line pipeline. A user provides one seed company domain, such as `stripe.com`, and the script runs four stages:

```text
stripe.com
  -> Ocean.io finds similar company domains
  -> Prospeo finds senior decision makers at those companies
  -> Hunter.io resolves work emails
  -> Brevo sends personalized outreach emails after confirmation
```

The pipeline is intentionally sequential. Each stage produces data that becomes the input for the next stage. It also saves JSON output files after the major stages so you can inspect what happened.

## Project Structure

```text
outreach-pipeline/
  pipeline.py
  stages/
    ocean.py
    prospeo.py
    hunter.py
    brevo.py
  utils/
    helpers.py
  .env.example
  .gitignore
  requirements.txt
  README.md
  WALKTHROUGH.md
```

### `pipeline.py`

This is the main entry point. It handles:

- CLI argument parsing or interactive domain prompt.
- Stage orchestration.
- Stage-level try/except handling.
- Saving JSON outputs.
- The mandatory safety checkpoint before sending.
- Final send summary.

### `stages/ocean.py`

Stage 1 calls Ocean.io to find lookalike company domains for the seed domain.

The main function is:

```python
get_lookalike_companies(seed_domain: str) -> list[str]
```

It normalizes the seed domain, calls Ocean.io, extracts domains from the response, removes duplicates, limits results to 15, and raises a clear error if no lookalikes are found.

### `stages/prospeo.py`

Stage 2 calls Prospeo to find decision makers for the lookalike domains.

The main function is:

```python
get_decision_makers(domains: list[str]) -> list[dict[str, str]]
```

It caps the search at 10 domains, waits 1.1 seconds between calls, filters for senior titles, skips contacts without LinkedIn URLs, and deduplicates contacts by LinkedIn URL.

### `stages/hunter.py`

Stage 3 resolves work emails with Hunter.io.

The main function is:

```python
resolve_emails(contacts: list[dict[str, str]]) -> list[dict[str, str]]
```

It deduplicates contacts, calls Hunter.io's email finder with domain plus first and last name, and logs any contacts that cannot be resolved.

### `stages/brevo.py`

Stage 4 sends personalized emails through Brevo.

The main function is:

```python
send_emails(leads: list[dict[str, str]]) -> dict[str, int]
```

It builds the email subject and body per lead, sends through Brevo's transactional email endpoint, sleeps 0.5 seconds between sends, appends successful sends to `sent_emails.json`, logs failures, and continues even if one email fails.

### `utils/helpers.py`

This contains shared plumbing:

- `.env` helpers.
- Domain normalization.
- Name splitting.
- JSON saving and append logging.
- Error logging to `errors.log`.
- HTTP requests with 429 retry/backoff.
- Flexible nested response parsing.
- Deduplication helpers.

## Setup

From the project directory:

```bash
cd C:\Users\chara\Desktop\task\outreach-pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

In PowerShell, activation needs the leading `.\` and the PowerShell script name. If script execution is blocked, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If virtual environment creation was interrupted with `KeyboardInterrupt`, remove the partial `.venv` folder and rerun `python -m venv .venv`.

Then open `.env` and fill in your real keys.

## Environment Variables

Required for the full pipeline:

```text
OCEAN_API_KEY=your_ocean_key
PROSPEO_API_KEY=your_prospeo_key
BREVO_API_KEY=your_brevo_key
SENDER_EMAIL=charan@yourdomain.com
SENDER_NAME=Charan Kasula
HUNTER_API_KEY=your_hunter_key
```

Optional API tuning:

```text
OCEAN_BASE_URL=https://api.ocean.io
OCEAN_ENDPOINT=/v3/search/companies
OCEAN_AUTH_HEADER=x-api-token
OCEAN_LOOKALIKE_LIMIT=15

PROSPEO_BASE_URL=https://api.prospeo.io
PROSPEO_ENDPOINT=/search-person
PROSPEO_MAX_DOMAINS=10
PROSPEO_CONTACTS_PER_DOMAIN=5

HUNTER_BASE_URL=https://api.hunter.io/v2
BREVO_BASE_URL=https://api.brevo.com/v3
```

## How To Run

With a domain argument:

```bash
python pipeline.py stripe.com
```

Without an argument:

```bash
python pipeline.py
```

The script will prompt:

```text
Enter seed domain:
```

## Full Execution Flow

### 1. Input Domain

The user provides a domain. `pipeline.py` normalizes it using `normalize_domain()`.

Examples:

```text
https://www.stripe.com/pricing -> stripe.com
stripe.com -> stripe.com
```

If the value cannot be normalized, the pipeline exits before using any API credits.

### 2. Stage 1: Ocean.io Lookalikes

Console output:

```text
[Stage 1] Searching for companies similar to stripe.com...
[Stage 1] Found 12 lookalike companies.
```

Output file:

```text
stage1_domains.json
```

Example shape:

```json
[
  "adyen.com",
  "braintreepayments.com",
  "razorpay.com"
]
```

Important behavior:

- Limits output to 15 domains.
- Removes duplicate domains case-insensitively.
- Exits clearly if Ocean returns no usable domains.

### 3. Stage 2: Prospeo Decision Makers

Console output:

```text
[Stage 2] Finding decision makers across 12 companies...
[Stage 2] Found 28 contacts (CEO, VP, CTO level).
```

Output file:

```text
stage2_contacts.json
```

Example shape:

```json
[
  {
    "name": "John Smith",
    "title": "CEO",
    "linkedin_url": "https://linkedin.com/in/johnsmith",
    "company": "HubSpot",
    "domain": "hubspot.com"
  }
]
```

Important behavior:

- Uses a maximum of 10 domains by default.
- Sleeps 1.1 seconds between Prospeo requests.
- Retries 429 rate limits with exponential backoff.
- Skips domains with no usable contacts.
- Skips contacts without LinkedIn URLs.
- Keeps senior titles only.

The senior title filter currently matches:

```text
CEO, CTO, CFO, COO, Chief, VP, Vice President, Director, Founder, President
```

### 4. Stage 3: Email Resolution

Console output:

```text
[Stage 3] Resolving work emails...
[Stage 3] Verified 19 emails. (9 unresolvable - skipped)
```

Output file:

```text
stage3_leads.json
```

Example shape:

```json
[
  {
    "name": "John Smith",
    "title": "CEO",
    "email": "john@hubspot.com",
    "company": "HubSpot",
    "domain": "hubspot.com",
    "linkedin_url": "https://linkedin.com/in/johnsmith"
  }
]
```

Important behavior:

- Deduplicates LinkedIn URLs before calling resolver APIs.
- Uses Hunter.io when `HUNTER_API_KEY` is configured.
- Looks up email by company domain, first name, and last name.
- Skips unresolved contacts instead of crashing.
- Logs skipped contacts to `errors.log`.

If zero emails are resolved, the script warns the user and asks whether to abort.

### 5. Mandatory Safety Checkpoint

Before sending any email, the script prints a summary:

```text
============================================
           OUTREACH PIPELINE SUMMARY
============================================
  Seed domain          : stripe.com
  Lookalike companies  : 12
  Decision makers found: 28
  Verified emails      : 19
============================================

Preview (first 3 contacts):
  1. John Smith (CEO) @ HubSpot - john@hubspot.com
  2. Sarah Lee (VP Sales) @ Pipedrive - sarah@pipedrive.com
  3. Raj Patel (CTO) @ Razorpay - raj@razorpay.com
  ... and 16 more

WARNING: About to send 19 cold emails. This cannot be undone.

Proceed? (y/n):
```

Only this exact input sends emails:

```text
y
```

Any other input exits:

```text
Aborted. No emails sent.
```

This is the main protection against accidental outreach.

### 6. Stage 4: Brevo Sending

Console output:

```text
[Stage 4] Sending personalized emails...
[Stage 4] Done. Sent: 17; Failed: 2
```

Successful sends are appended to:

```text
sent_emails.json
```

Example shape:

```json
[
  {
    "timestamp": "2026-06-07T08:30:00+00:00",
    "email": "john@hubspot.com",
    "name": "John Smith",
    "company": "HubSpot",
    "domain": "hubspot.com",
    "message_id": "..."
  }
]
```

Failed sends are logged to:

```text
errors.log
```

One failed email does not stop the rest of the sends.

## Email Personalization

Each email uses the lead's first name and company.

Subject:

```text
Quick question, John
```

Body:

```text
Hi John,

I came across HubSpot while researching companies doing interesting work
in the space - impressive what your team has built.

I'm Charan, a full-stack AI engineer. I've been building automation systems
that help teams eliminate manual steps in their workflows - recently shipped
a multi-agent pipeline on AWS that handles end-to-end orchestration with
zero human handoff.

Would love to explore if there's a fit. Open to a quick 15-minute call this
week?

Best,
Charan
```

## Output Files

These files are generated during pipeline runs:

```text
stage1_domains.json
stage2_contacts.json
stage3_leads.json
sent_emails.json
errors.log
```

They are ignored by git because they may contain personal data, prospect data, API error details, and send logs.

## Rate Limits And Safeguards

Ocean.io:

- One company lookalike search per run.
- Maximum 15 output domains.

Prospeo:

- Maximum 10 domains by default.
- 1.1 second delay between requests.
- 429 retry backoff: 2 seconds, 4 seconds, 8 seconds.

Hunter.io:

- Uses domain plus first and last name.
- Skips unresolved contacts.
- 429 retry backoff: 2 seconds, 4 seconds, 8 seconds.

Brevo:

- 0.5 second delay between email sends.
- Logs each successful send.
- Logs each failure and continues.

## Error Handling Philosophy

The pipeline should stop only when continuing would make no sense or could waste credits.

It exits early when:

- The seed domain is invalid.
- Stage 1 returns no lookalike domains.
- Stage 2 returns zero contacts across all domains.
- A required API key for the current stage is missing.

It skips individual records when:

- One Prospeo domain fails.
- A contact has no LinkedIn URL.
- An email cannot be resolved.
- One Brevo send fails.

All stage errors are written to:

```text
errors.log
```

## Demo Checklist

Before a live demo:

1. Install dependencies with `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Fill real API keys.
4. Confirm the Brevo sender email is verified.
5. Confirm the Hunter.io API key is present.
6. Run with a seed domain:

```bash
python pipeline.py stripe.com
```

7. Inspect the checkpoint carefully.
8. Type `y` only when you actually want emails sent.

For a safer demo, you can stop at the checkpoint by typing anything other than `y`.

## Common Issues

### `ModuleNotFoundError: No module named 'requests'`

Dependencies are not installed. Run:

```bash
pip install -r requirements.txt
```

### `Missing required environment variable`

The relevant API key or sender value is missing from `.env`.

### Ocean.io returns no domains

Check:

- The seed domain is valid.
- The API key has credits.
- `OCEAN_AUTH_HEADER` matches your account's API docs.
- `OCEAN_ENDPOINT` matches your account's API docs.

### Prospeo returns no contacts

Check:

- Prospeo API key is valid.
- The searched domains have indexed people.
- The seniority/title filters are not too strict for the target market.
- You have not hit the daily request limit.

### Stage 3 resolves zero emails

Check:

- `HUNTER_API_KEY` is present and valid.
- The Hunter.io account has remaining searches.
- Contact names and domains are clean.

### Brevo sending fails

Check:

- `BREVO_API_KEY` is valid.
- `SENDER_EMAIL` is verified in Brevo.
- The account has remaining transactional email quota.
- Recipient emails are valid.

## How To Extend It

Useful future improvements:

- Add a dry-run mode that exercises Stages 1-3 but never sends.
- Add CSV export for leads.
- Add a campaign name to group output files per run.
- Add unit tests with mocked API responses.
- Add richer email templates based on contact title.
- Add company enrichment before email generation.

Keep the safety checkpoint in place for any future version that can send emails.
