"""Merge messy contact lists into one clean, de-duplicated spreadsheet.

Usage:
    python clean_contacts.py sample_data/*.csv
    python clean_contacts.py a.csv b.csv --out results

Writes three files to the output folder:
    clean_contacts.csv   one row per person, standardized
    needs_review.csv     rows with problems a human should check
    report.txt           what was changed and why

Standard library only. Original files are never modified.
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

# Header spellings seen in real exports -> our column name
HEADER_ALIASES = {
    "name": ["name", "full name", "contact name", "customer name"],
    "email": ["email", "e-mail", "email address", "e-mail address"],
    "phone": ["phone", "phone #", "phone number", "mobile", "cell", "tel"],
    "state": ["state", "state_province", "province", "region"],
    "signup_date": ["signup date", "date joined", "date_joined", "created", "joined"],
    "company": ["company", "organization", "organisation", "business"],
}
COLUMNS = list(HEADER_ALIASES)

STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
STATE_CODES = set(STATES.values())

DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y",
                "%b %d %Y", "%B %d %Y", "%d %b %Y"]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")


def map_headers(headers):
    mapping = {}
    for raw in headers:
        key = raw.strip().lower()
        for col, aliases in HEADER_ALIASES.items():
            if key in aliases:
                mapping[raw] = col
    return mapping


def clean_name(value):
    v = " ".join(value.split())
    if "," in v:  # "SMITH, JOHN" -> "JOHN SMITH"
        last, first = [p.strip() for p in v.split(",", 1)]
        v = f"{first} {last}"
    # Title-case each part, keeping O'Brien / Smith-Jones correct
    return " ".join("-".join(p[:1].upper() + p[1:].lower() if "'" not in p
                             else "'".join(s.capitalize() for s in p.split("'"))
                             for p in w.split("-")) for w in v.split())


def clean_email(value):
    v = value.strip().lower()
    return v, (None if not v or EMAIL_RE.match(v) else "invalid email")


def clean_phone(value):
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if not digits:
        return "", None
    if len(digits) != 10:
        return value.strip(), "phone is not 10 digits"
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}", None


def clean_state(value):
    v = value.strip()
    if not v:
        return "", None
    if v.upper() in STATE_CODES:
        return v.upper(), None
    code = STATES.get(v.lower())
    return (code, None) if code else (v, "unknown state")


def clean_date(value):
    v = " ".join(value.split())
    if not v:
        return "", None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    return v, "unreadable or impossible date"


def clean_row(raw):
    row, problems = {}, []
    row["name"] = clean_name(raw.get("name", ""))
    for col, fn in [("email", clean_email), ("phone", clean_phone),
                    ("state", clean_state), ("signup_date", clean_date)]:
        row[col], problem = fn(raw.get(col, ""))
        if problem:
            problems.append(problem)
    row["company"] = " ".join(raw.get("company", "").split())
    return row, problems


def merge(existing, new):
    """Fill blanks in `existing` from `new`; keep the longer company name."""
    for col in COLUMNS:
        if not existing[col] and new[col]:
            existing[col] = new[col]
    if len(new["company"]) > len(existing["company"]):
        existing["company"] = new["company"]


def main():
    ap = argparse.ArgumentParser(description="Merge and clean contact CSVs.")
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("output"))
    args = ap.parse_args()

    people, review, log = [], [], []
    by_email, by_phone = {}, {}
    rows_in = blank = dupes = 0

    for path in args.files:
        if not path.exists():
            sys.exit(f"File not found: {path}")
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            mapping = map_headers(reader.fieldnames or [])
            for line_no, raw_row in enumerate(reader, start=2):
                raw = {mapping[k]: (v or "") for k, v in raw_row.items() if k in mapping}
                rows_in += 1
                if not any(v.strip() for v in raw.values()):
                    blank += 1
                    continue
                row, problems = clean_row(raw)
                where = f"{path.name} line {line_no}"
                if problems:
                    review.append({**row, "source": where, "problems": "; ".join(problems)})
                    log.append(f"REVIEW  {where}: {', '.join(problems)}")
                    continue

                match = (by_email.get(row["email"]) if row["email"] else None) or \
                        (by_phone.get(row["phone"]) if row["phone"] else None)
                if match is not None:
                    merge(match, row)
                    dupes += 1
                    log.append(f"MERGED  {where}: duplicate of {match['name']}")
                else:
                    people.append(row)
                    match = row
                if match["email"]:
                    by_email[match["email"]] = match
                if match["phone"]:
                    by_phone[match["phone"]] = match

    args.out.mkdir(exist_ok=True)
    people.sort(key=lambda r: r["name"].split()[-1] if r["name"] else "")
    with (args.out / "clean_contacts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(people)
    with (args.out / "needs_review.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS + ["source", "problems"])
        w.writeheader()
        w.writerows(review)

    summary = [
        f"Files read:        {len(args.files)}",
        f"Rows read:         {rows_in}",
        f"Blank rows:        {blank}",
        f"Duplicates merged: {dupes}",
        f"Needs review:      {len(review)}",
        f"Clean contacts:    {len(people)}",
    ]
    (args.out / "report.txt").write_text("\n".join(summary + ["", *log]) + "\n", encoding="utf-8")
    print("\n".join(summary))
    print(f"\nSaved to {args.out.resolve()}")


if __name__ == "__main__":
    main()
