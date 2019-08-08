"""
Convert the json dump retrievable from https://www.trumf.no/personvern/bestill-innsyn to csv.
"""

import sys
import csv
import json
from datetime import datetime


def to_number(nor_number_str):
    return float(nor_number_str.replace(",", "."))


def to_date(date_str):
    try:
        date = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
    except ValueError:
        date = datetime.strptime(date_str, "%d.%m.%Y")

    return date


def to_transactions(trumf_receipts):
    transactions = []
    for receipt in trumf_receipts:
        date_str = receipt["dato"]
        date = to_date(date_str)

        common = {
            "date": date,
            "receipt_id": receipt["kvitteringsnummer"],
            "store_chain": receipt["kjede"],
            "store_name": receipt["butikknavn"]
        }

        for varelinje in receipt["varelinjer"]:
            line = {
                "item": varelinje["varenavn"],
                "count": to_number(varelinje["vareAntallVekt"]),
                "amount": to_number(varelinje["vareBelop"]),  # total amount, not per count
            }
            transactions.append({**common, **line})

    return transactions


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print("Pipe input json file to stdin. Output written to stdout")
        exit(1)

    trumf_receipts = json.load(sys.stdin)
    transactions = to_transactions(trumf_receipts)

    # Write to csv
    columns = list(transactions[0].keys())
    writer = csv.DictWriter(sys.stdout, columns, dialect="unix")
    writer.writeheader()
    writer.writerows(transactions)
