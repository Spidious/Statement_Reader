from dataclasses import dataclass
from datetime import date, datetime
import re

import pypdf


@dataclass
class Transaction:
    date: date
    description: str
    amount: float
    balance: float
    category: str = ""


# Matches any line that looks like a column-header row: must contain DATE plus at
# least one other known column keyword, in any order.
_HEADER_RE = re.compile(
    r"(?=.*\bDATE\b)(?=.*\b(?:DESCRIPTION|CATEGORY|AMOUNT|BALANCE|TYPE|DETAILS)\b)",
    re.IGNORECASE,
)
_DATE_START_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b", re.IGNORECASE)
# Captures: month  day  description  category  amount  balance
# The amount is preceded by "- $" where "-" is the debit indicator
_TRANSACTION_RE = re.compile(
    r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\s+"
    r"(.+?)\s+(\w+)\s+-\s+\$?([\d,]+\.\d{2})\s+\$?([\d,]+\.\d{2})\s*$",
    re.IGNORECASE,
)


class Reader:
    def __init__(self, f_path: str):
        self.file_path = f_path

    def read(self) -> list[Transaction]:
        text = self._extract_text()
        return self._parse_transactions(text)

    def _extract_text(self) -> str:
        with open(self.file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _parse_transactions(self, text: str) -> list[Transaction]:
        lines = text.splitlines()

        # Start parsing only after the header row
        header_idx = next(
            (i for i, ln in enumerate(lines) if _HEADER_RE.search(ln)),
            None,
        )
        if header_idx is None:
            return []

        # Join wrapped continuation lines into single transaction strings
        joined: list[str] = []
        current: str | None = None
        for line in lines[header_idx + 1:]:
            stripped = line.strip()
            if not stripped:
                continue
            if _DATE_START_RE.match(stripped):
                if current is not None:
                    joined.append(current)
                current = stripped
            elif current is not None:
                current = current + " " + stripped
        if current is not None:
            joined.append(current)

        transactions = []
        for tline in joined:
            m = _TRANSACTION_RE.match(tline)
            if not m:
                continue
            month, day, description, category, amount_str, balance_str = m.groups()
            transactions.append(Transaction(
                date=_parse_date(f"{month} {day}"),
                description=description.strip(),
                category=category,
                amount=_parse_amount(amount_str),
                balance=_parse_amount(balance_str),
            ))
        return transactions


def _parse_date(month_day: str) -> date:
    d = datetime.strptime(month_day.strip(), "%b %d")
    return date(date.today().year, d.month, d.day)


def _parse_amount(value: str) -> float:
    return float(value.replace("$", "").replace(",", ""))


if __name__ == '__main__':
    # import sys
    # if len(sys.argv) < 2:
    #     print("Usage: python main.py <path_to_statement.pdf>")
    #     sys.exit(1)

    reader = Reader("/home/luke/Downloads/statement.pdf")
    transactions = reader.read()
    for t in transactions:
        print(t)

