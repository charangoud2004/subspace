# 🚀 Automated B2B Cold Outreach Pipeline

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Intelligent, automated lead generation and outreach system**  
> Takes a single seed company domain → finds similar companies → identifies decision-makers → verifies emails → sends personalized outreach

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Pipeline Stages](#-pipeline-stages)
- [Output Files](#-output-files)
- [API Rate Limits](#-api-rate-limits)
- [Safety Features](#-safety-features)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This Python CLI tool automates the entire B2B cold outreach workflow by orchestrating four powerful APIs:

1. **Ocean.io** - Finds lookalike companies based on your seed domain
2. **Prospeo** - Identifies C-suite and VP-level decision-makers
3. **Hunter.io** - Verifies and resolves work email addresses
4. **Brevo** - Sends personalized outreach emails

**Perfect for:** Sales teams, growth hackers, business development professionals, and entrepreneurs looking to scale their outreach efforts.

---

## ✨ Features

- ✅ **Automated lead discovery** - Find companies similar to your ideal customer profile
- ✅ **Decision-maker targeting** - Focus on CEOs, CTOs, VPs, Directors, Founders
- ✅ **Email verification** - Ensures high deliverability with Hunter.io validation
- ✅ **Personalized messaging** - Dynamic email templates with recipient details
- ✅ **Safety checkpoint** - Manual review and approval before sending any emails
- ✅ **Rate limiting** - Respects API quotas automatically
- ✅ **Error handling** - Comprehensive logging with timestamps
- ✅ **Deduplication** - Prevents sending duplicate emails
- ✅ **Flexible configuration** - Environment-based settings for easy deployment

---

## 🔄 How It Works

```
┌─────────────────┐
│  Input Domain   │ (e.g., stripe.com)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ocean.io      │ → Finds 10-15 lookalike companies
│  (Stage 1)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Prospeo       │ → Identifies decision-makers
│  (Stage 2)      │   (CEOs, CTOs, VPs, Directors)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Hunter.io     │ → Verifies work emails
│  (Stage 3)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Safety Check   │ → Manual approval required
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Brevo       │ → Sends personalized emails
│  (Stage 4)      │
└─────────────────┘
```

---

## 🛠️ Prerequisites

- **Python 3.8+** installed on your system
- **API Keys** from:
  - [Ocean.io](https://ocean.io/) - Company intelligence platform
  - [Prospeo](https://prospeo.io/) - Contact finder
  - [Hunter.io](https://hunter.io/) - Email verifier
  - [Brevo](https://www.brevo.com/) (formerly Sendinblue) - Email sender

---

## 📥 Installation

### 1. Clone the repository

```bash
git clone https://github.com/charangoud2004/subspace.git
cd subspace/outreach-pipeline
```

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Note:** If PowerShell blocks activation, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create environment file

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 2. Add your API keys to `.env`

```env
# Ocean.io - Find lookalike companies
OCEAN_API_KEY=your_ocean_api_key_here

# Prospeo - Find decision-makers
PROSPEO_API_KEY=your_prospeo_api_key_here

# Hunter.io - Verify emails
HUNTER_API_KEY=your_hunter_api_key_here

# Brevo - Send emails
BREVO_API_KEY=your_brevo_api_key_here
SENDER_EMAIL=your-verified-email@domain.com
SENDER_NAME=Your Name
```

### 3. API Key Sources

| Service | Where to find API key |
|---------|----------------------|
| **Ocean.io** | Dashboard → Settings → API Tokens |
| **Prospeo** | Dashboard → API Management |
| **Hunter.io** | Dashboard → API → API Keys |
| **Brevo** | Settings → SMTP & API → API Keys |

> ⚠️ **Important:** Your `SENDER_EMAIL` must be verified in Brevo before sending emails.

---

## 🚀 Usage

### Basic usage (with seed domain)

```bash
python pipeline.py stripe.com
```

### Interactive mode (prompt for domain)

```bash
python pipeline.py
# You'll be prompted: Enter seed domain: 
```

### Example output

```
[Stage 1] Searching for companies similar to stripe.com...
[Stage 1] Found 15 lookalike companies.

[Stage 2] Finding decision makers across 15 companies...
[Stage 2] Found 23 contacts (CEO, VP, CTO level).

[Stage 3] Resolving work emails...
[Stage 3] Verified 18 emails. (5 unresolvable - skipped)

[Checkpoint] Review summary before sending...

============================================
           OUTREACH PIPELINE SUMMARY
============================================
  Seed domain          : stripe.com
  Lookalike companies  : 15
  Decision makers found: 23
  Verified emails      : 18
============================================

Preview (first 3 contacts):
  1. John Smith (CEO) @ Acme Corp - john.smith@acmecorp.com
  2. Jane Doe (CTO) @ Tech Solutions - jane.doe@techsolutions.com
  3. Bob Wilson (VP Engineering) @ DataFlow - bob.wilson@dataflow.io
  ... and 15 more

WARNING: About to send 18 cold emails. This cannot be undone.

Proceed? (y/n): 
```

---

## 📊 Pipeline Stages

### Stage 1: Ocean.io - Lookalike Discovery
- Finds 10-15 companies similar to your seed domain
- Uses lookalike search algorithms
- Outputs: `stage1_domains.json`

### Stage 2: Prospeo - Decision-Maker Identification
- Searches up to 10 domains for senior contacts
- Targets: CEO, CTO, CFO, VP, Director, Founder, President
- Requires LinkedIn profile URLs
- Outputs: `stage2_contacts.json`

### Stage 3: Hunter.io - Email Verification
- Resolves work emails using name + domain
- Validates email deliverability
- Outputs: `stage3_leads.json`

### Stage 4: Brevo - Personalized Outreach
- Sends customized emails to verified leads
- Rate-limited to respect quotas
- Outputs: `sent_emails.json`

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `stage1_domains.json` | List of lookalike company domains |
| `stage2_contacts.json` | Decision-maker contacts with LinkedIn URLs |
| `stage3_leads.json` | Verified leads with email addresses |
| `sent_emails.json` | Log of successfully sent emails with timestamps |
| `errors.log` | Error log with timestamps and stage information |

---

## ⏱️ API Rate Limits

| Service | Free Tier Limit | Pipeline Behavior |
|---------|----------------|-------------------|
| **Ocean.io** | Limited credits | 1 search, max 15 results |
| **Prospeo** | 50 requests/day, 1/second | Max 10 domains, 1.1s delay between calls |
| **Hunter.io** | 25 searches/month | 1.0s delay between calls |
| **Brevo** | 300 emails/day | 0.5s delay between sends |

---

## 🛡️ Safety Features

### Mandatory Checkpoint
Before any emails are sent, the pipeline shows:
- Complete summary of domains, contacts, and emails
- Preview of first 3 recipients
- Warning about irreversibility

**Only typing exactly `y` will proceed** - any other input aborts.

### Error Handling
- All errors logged to `errors.log` with timestamps
- Failed API calls trigger retries with exponential backoff
- Invalid data is skipped with warnings

### Deduplication
- Domains, contacts, and emails are deduplicated
- Prevents accidental duplicate sends

---

## 🔧 Troubleshooting

### Virtual environment issues
```bash
# If venv creation was interrupted, delete and recreate
rmdir /s .venv  # Windows
rm -rf .venv    # macOS/Linux
python -m venv .venv
```

### PowerShell execution policy error
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### API authentication errors
- Verify API keys are correctly copied to `.env`
- Check if Ocean.io requires Bearer auth: `OCEAN_AUTH_HEADER=Authorization`
- Ensure Brevo sender email is verified

### No results from Prospeo
- Check if domain search endpoint is needed: `PROSPEO_ENDPOINT=/domain-search`
- Verify API key has search permissions

### Import errors
```bash
pip install -r requirements.txt --upgrade
```

---

## 📂 Project Structure

```
outreach-pipeline/
├── pipeline.py              # Main orchestrator
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .env                    # Your API keys (gitignored)
├── stages/
│   ├── __init__.py
│   ├── ocean.py           # Stage 1: Lookalike finder
│   ├── prospeo.py         # Stage 2: Decision-maker finder
│   ├── hunter.py          # Stage 3: Email verifier
│   └── brevo.py           # Stage 4: Email sender
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Shared utilities
├── stage1_domains.json    # Output from Stage 1
├── stage2_contacts.json   # Output from Stage 2
├── stage3_leads.json      # Output from Stage 3
├── sent_emails.json       # Sent email log
├── errors.log             # Error log
└── README.md              # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Charan Goud**

- GitHub: [@charangoud2004](https://github.com/charangoud2004)

---

## ⭐ Acknowledgments

- Ocean.io for company intelligence
- Prospeo for contact discovery
- Hunter.io for email verification
- Brevo for reliable email delivery

---

## 📧 Support

If you have any questions or run into issues, please open an issue on GitHub or reach out via email.

---

**Happy Outreaching! 🎯**
