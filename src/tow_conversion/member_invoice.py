"""Module to define the MemberInvoiceItem class for tow billing information and method to save"""
from datetime import datetime, timedelta
from pathlib import Path
import logging
import csv
from enum import Enum
from tow_conversion.tow_data import TowDataItem
from tow_conversion.invoice import Invoice
from tow_conversion.name import Name

log = logging.getLogger('MemberInvoice')


class Product(Enum):
    """Enum to represent different products or services."""
    TOW = 'Towing'
    GLIDER = 'Glider Rental'


class Classification(Enum):
    """Enum to represent different classifications for the MemberInvoiceItem."""
    TOW = "TOW"
    GLIDER = "GLIDER"


class MemberInvoiceItem(Invoice):
    """Class to hold member invoice data for a tow."""

    @classmethod
    def from_tow_data(cls, tow_data: TowDataItem, log_unbillable_tow_tickets: bool = True) -> list['MemberInvoiceItem']:
        """
        Create a MemberInvoiceItem from a TowDataItem.

        Parameters
        ----------
        tow_data : TowDataItem
            The TowDataItem instance containing the tow data.
        log_unbillable_tow_tickets : bool
            Optional, default=True
            If True, log a warning if the tow ticket is not completed and no items are created.
            If False, suppress warnings for unbillable tow tickets.

        Returns
        -------
        list[MemberInvoiceItem]
            0-2 MemberInvoiceItem's populated with data from the TowDataItem containing:
            - Item for Glider Rental if billable rental is True
            - Item for Towing if billable tow is True
        """
        items: list[MemberInvoiceItem] = list()

        if not cls.is_tow_ticket_completed(tow_data, log_warnings=log_unbillable_tow_tickets):
            return items

        if tow_data.billable_rental:
            item = cls(
                name=tow_data.pilot,
                # Set invoice_date to now, due_date to 30 days after invoice_date
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Glider: {tow_data.glider_id}, Glider Time: {tow_data.glider_time:.1f} hours',  # pylint: disable=line-too-long
                product=Product.GLIDER,
                classification=Classification.GLIDER,
                amount=tow_data.rental_fee
            )
            items.append(item)

        if tow_data.billable_tow:
            item = cls(
                name=tow_data.pilot,
                # Set invoice_date to now, due_date to 30 days after invoice_date
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}',
                product=Product.TOW,
                classification=Classification.TOW,
                amount=tow_data.tow_fee
            )
            items.append(item)

        return items


def export_member_invoices_to_csv(filename: str | Path, invoices: list[MemberInvoiceItem]) -> None:
    """
    Save the billing data to a CSV file.

    Parameters
    ----------
    filename : str
        The path to the CSV file where the invoice data will be saved.
    items : list[MemberInvoiceItem]
        An list of MemberInvoiceItem objects representing the invoice items to be saved.

    Returns
    -------
    None

    Notes
    -----
    This method writes the provided invoice items to a CSV file using the specified filename.
    """
    log.info("Exporting member invoices to %s", filename)
    invoices_by_pilot: dict[Name, list[MemberInvoiceItem]] = dict()
    for item in invoices:
        key = item.name
        # Group items by display name (pilot)
        if key not in invoices_by_pilot:
            invoices_by_pilot[key] = list()
        invoices_by_pilot[key].append(item)

    headers = ['Display Name',
               'Invoice Date',
               'Due Date',
               'Service Date',
               'Description or Memo',
               'Product',
               'CLASS',
               'SORT Last Name',
               'SORT First Name',
               'Sum of Tow Fee']

    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for pilot, pilot_invoices in sorted(invoices_by_pilot.items()):
            for idx, item in enumerate(sorted(pilot_invoices, key=lambda x: x.service_date)):
                if idx == 0:
                    display_name = pilot
                    invoice_date = item.invoice_date.strftime('%m/%d/%Y')
                    due_date = item.due_date.strftime('%m/%d/%Y')
                else:
                    display_name = ''
                    invoice_date = ''
                    due_date = ''
                row = [
                    display_name,
                    invoice_date,
                    due_date,
                    item.service_date.strftime('%m/%d/%Y %H:%M'),
                    item.description,
                    item.product.value,
                    item.classification.value,
                    item.name.last,
                    item.name.first,
                    f"${item.amount:.2f}"
                ]
                writer.writerow(row)
    log.info("Member invoices exported successfully")
