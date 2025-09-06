"""Command-line interface for converting tow tickets to member invoices and vendor bills."""
import argparse
import logging
from pathlib import Path
import sys

from tow_conversion import convert_tow_ticket_to_all_invoices

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def main() -> None:
    """Handle command-line arguments and invoke conversion functions."""
    parser = argparse.ArgumentParser(
        description="Convert a tow ticket CSV file to member invoice and vendor bill CSV files."
    )
    parser.add_argument(
        "tow_ticket_csv",
        type=Path,
        help="Input tow ticket CSV file"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output files if they already exist"
    )
    args = parser.parse_args()

    input_file = args.tow_ticket_csv.resolve()
    if not input_file.exists():
        print(
            f"Error: Input file {input_file} does not exist.", file=sys.stderr)
        sys.exit(1)

    base = input_file.with_suffix("")
    member_invoice_file = base.parent / f"{base.name}_member_invoice.csv"
    vendor_bill_file = base.parent / f"{base.name}_vendor_bill.csv"

    for output_file in [member_invoice_file, vendor_bill_file]:
        if output_file.exists() and not args.overwrite:
            print(
                f"Error: Output file {output_file} already exists. Use --overwrite to overwrite.", file=sys.stderr)
            sys.exit(1)

    convert_tow_ticket_to_all_invoices(
        tow_ticket_file=input_file,
        member_invoice_file=member_invoice_file,
        vendor_invoice_file=vendor_bill_file
    )
    print(f"Member invoice written to {member_invoice_file}")
    print(f"Vendor bill written to {vendor_bill_file}")


if __name__ == "__main__":
    main()
