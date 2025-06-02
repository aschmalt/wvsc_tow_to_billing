"""Converter module to convert tow ticket data to billing data."""
from collections.abc import Generator
import csv
from pathlib import Path
import logging


def convert_tow_row_to_billing_row(tow_row: dict[str, str]) -> dict[str: str]:
    """Convert a tow row to a billing row."""
    return dict()


def read_tow_file(file_path: str | Path) -> Generator[dict[str, str], str | Path, None]:
    """Read a tow file and return a list of tow rows."""
    with open(file=file_path, mode='r') as file:
        reader = csv.DictReader(f=file)
        for row in reader:
            yield row
