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


def convert_tow_ticket_to_all_invoices(tow_ticket_file: str | Path,
                                       member_invoice_file: str | Path,
                                       vendor_invoice_file: str | Path) -> None:
    """
    Converts tow ticket data into member invoices and vendor bills, then exports them to CSV files.
    Parameters
    ----------
    tow_ticket_file : str or Path
        Path to the CSV file containing tow ticket data.
    member_invoice_file : str or Path
        Path where the generated member invoices CSV will be saved.
    vendor_invoice_file : str or Path
        Path where the generated vendor bills CSV will be saved.

    Returns
    -------
    None
        This function does not return a value. It writes the output to the specified CSV files.

    Notes
    -----
    - Reads tow ticket data, processes it into member invoices and vendor bills.
    - Unbillable tow tickets are not logged during member invoice creation to avoid duplicate warnings.
    - Output files are overwritten if they already exist.
    """
    all_tow_data = TowDataItem.read_from_tow_csv(tow_ticket_file)
    vendor_bills: list[VendorBillItem] = list()
    member_invoices: list[MemberInvoiceItem] = list()
    for tow_data in all_tow_data:
        vendor_bills.extend(VendorBillItem.from_tow_data(tow_data))
        member_invoices.extend(MemberInvoiceItem.from_tow_data(
            tow_data, log_unbillable_tow_tickets=False))

    export_member_invoices_to_csv(invoices=member_invoices,
                                  filename=member_invoice_file)

    export_vendor_bills_to_csv(invoices=vendor_bills,
                               filename=vendor_invoice_file)
