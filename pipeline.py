"""CLI entry point that orchestrates the full B2B cold outreach pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from stages.brevo import send_emails
from stages.hunter import resolve_emails
from stages.ocean import get_lookalike_companies
from stages.prospeo import get_decision_makers
from utils.helpers import dedupe_preserve_order, log_error, normalize_domain, save_json


def _get_seed_domain(argv: list[str]) -> str:
    if len(argv) > 1:
        return argv[1].strip()
    return input("Enter seed domain: ").strip()


def _print_checkpoint(
    seed_domain: str,
    domains: list[str],
    contacts: list[dict[str, str]],
    leads: list[dict[str, str]],
) -> bool:
    print("\n============================================")
    print("           OUTREACH PIPELINE SUMMARY")
    print("============================================")
    print(f"  Seed domain          : {seed_domain}")
    print(f"  Lookalike companies  : {len(domains)}")
    print(f"  Decision makers found: {len(contacts)}")
    print(f"  Verified emails      : {len(leads)}")
    print("============================================\n")
    print("Preview (first 3 contacts):")
    for index, lead in enumerate(leads[:3], start=1):
        print(
            f"  {index}. {lead.get('name', 'Unknown')} ({lead.get('title', 'Unknown title')}) "
            f"@ {lead.get('company', lead.get('domain', 'Unknown company'))} - {lead.get('email', '')}"
        )
    remaining = len(leads) - 3
    if remaining > 0:
        print(f"  ... and {remaining} more")
    print(f"\nWARNING: About to send {len(leads)} cold emails. This cannot be undone.\n")
    return input("Proceed? (y/n): ") == "y"


def _abort(message: str, exit_code: int = 1) -> None:
    print(message)
    raise SystemExit(exit_code)


def _warn_zero_emails() -> None:
    print("[Stage 3] WARNING: 0 verified emails were resolved.")
    if input("Abort now? (y/n): ") == "y":
        _abort("Aborted. No emails sent.", 0)


def run(seed_domain: str) -> dict[str, int]:
    normalized_seed = normalize_domain(seed_domain)
    if not normalized_seed:
        _abort(f"Invalid domain: {seed_domain!r}")

    try:
        print(f"[Stage 1] Searching for companies similar to {normalized_seed}...")
        domains = get_lookalike_companies(normalized_seed)
        save_json("stage1_domains.json", domains)
        print(f"[Stage 1] Found {len(domains)} lookalike companies.\n")
    except Exception as exc:
        log_error("Stage 1", str(exc))
        _abort(f"[Stage 1] Failed: {exc}")

    try:
        print(f"[Stage 2] Finding decision makers across {len(domains)} companies...")
        contacts = get_decision_makers(domains)
        save_json("stage2_contacts.json", contacts)
        if not contacts:
            _abort("[Stage 2] Found 0 contacts across all domains. Exiting.")
        print(f"[Stage 2] Found {len(contacts)} contacts (CEO, VP, CTO level).\n")
    except SystemExit:
        raise
    except Exception as exc:
        log_error("Stage 2", str(exc))
        _abort(f"[Stage 2] Failed: {exc}")

    try:
        print("[Stage 3] Resolving work emails...")
        leads = resolve_emails(contacts)
        save_json("stage3_leads.json", leads)
        unresolved = max(len(contacts) - len(leads), 0)
        print(f"[Stage 3] Verified {len(leads)} emails. ({unresolved} unresolvable - skipped)\n")
        if not leads:
            _warn_zero_emails()
    except SystemExit:
        raise
    except Exception as exc:
        log_error("Stage 3", str(exc))
        _abort(f"[Stage 3] Failed: {exc}")

    leads = dedupe_preserve_order(leads, key=lambda item: item.get("email", ""))
    print("[Checkpoint] Review summary before sending...")
    if not _print_checkpoint(normalized_seed, domains, contacts, leads):
        _abort("Aborted. No emails sent.", 0)

    try:
        print("\n[Stage 4] Sending personalized emails...")
        summary = send_emails(leads)
        print(f"[Stage 4] Done. Sent: {summary['sent']}; Failed: {summary['failed']}")
        return summary
    except Exception as exc:
        log_error("Stage 4", str(exc))
        _abort(f"[Stage 4] Failed: {exc}")


def main(argv: list[str] | None = None) -> None:
    run(_get_seed_domain(argv or sys.argv))


if __name__ == "__main__":
    main()
