"""Converter module to convert tow ticket data to billing data."""
from pathlib import Path
import logging
from tow_conversion import (TowDataItem,
                            MemberInvoiceItem,
                            export_member_invoices_to_csv,
                            VendorBillItem,
                            export_vendor_bills_to_csv)

log = logging.getLogger(__name__)


def convert_tow_ticket_to_member_invoice(tow_ticket_file: str | Path, output_file: str | Path) -> None:
    """
    Convert tow ticket data to member invoice format and save to a CSV file.

    Parameters
    ----------
    tow_ticket_file : Path
        Path to the input tow ticket CSV file.
    output_file : Path
        Path to the output member invoice CSV file.
    """
    log.info("Converting %s to %s", tow_ticket_file, output_file)

    all_tow_data = TowDataItem.read_from_tow_csv(tow_ticket_file)
    member_invoices: list[MemberInvoiceItem] = list()
    for tow_data in all_tow_data:
        member_invoices.extend(MemberInvoiceItem.from_tow_data(tow_data))

    export_member_invoices_to_csv(invoices=member_invoices,
                                  filename=output_file)


def convert_tow_ticket_to_vendor_bill(tow_ticket_file: str | Path, output_file: str | Path) -> None:
    """
    Convert tow ticket data to vendor bill format and save to a CSV file.

    Parameters
    ----------
    tow_ticket_file : Path
        Path to the input tow ticket CSV file.
    output_file : Path
        Path to the output vendor bill CSV file.
    """
    log.info("Converting %s to %s", tow_ticket_file, output_file)

    all_tow_data = TowDataItem.read_from_tow_csv(tow_ticket_file)
    vendor_bills: list[VendorBillItem] = list()
    for tow_data in all_tow_data:
        vendor_bills.extend(VendorBillItem.from_tow_data(tow_data))

    export_vendor_bills_to_csv(invoices=vendor_bills,
                               filename=output_file)
