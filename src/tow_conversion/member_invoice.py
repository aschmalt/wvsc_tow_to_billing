"""Module to define the MemberInvoice class for tow billing information and method to save"""
from collections.abc import Iterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
import csv
from enum import Enum
from tow_conversion import TowDataItem

log = logging.getLogger('MemberInvoice')


class Product(Enum):
    """Enum to represent different products or services."""
    TOW = 'Towing'
    GLIDER = 'Glider Rental'


class Classification(Enum):
    """Enum to represent different classifications for the MemberInvoiceItem."""
    TOW = "TOW"
    GLIDER = "GLIDER"


@dataclass
class MemberInvoiceItem:
    """Class to hold member invoice data for a tow."""
    display_name: str = field(
        metadata={"description": "Display name for who to bill in the invoice"})
    invoice_date: datetime = field(
        metadata={"description": "Date of the invoice in '%m/%d/%Y' format"})
    due_date: datetime = field(
        metadata={"description": "Due date for the invoice in '%m/%d/%Y' format"})
    service_date: datetime = field(
        metadata={"description": "Date of service in '%m/%d/%Y' format"})
    description: str = field(
        metadata={"description": "Description of the service provided"})
    product: Product = field(
        metadata={"description": "Product or service type"})
    classification: Classification = field(
        metadata={"description": "Classification of the service"})
    last_name: str = field(
        metadata={"description": "Last name of the member"})
    first_name: str = field(
        metadata={"description": "First name of the member"})
    amount: float = field(
        metadata={"description": "Amount charged for the service in dollars"})

    def __post_init__(self) -> None:
        """Post-initialization validation for the MemberInvoiceItem class."""
        if self.amount < 0:
            raise ValueError("Amount must be a non-negative value.")

    @classmethod
    def from_tow_data(cls, tow_data: TowDataItem) -> list['MemberInvoiceItem']:
        """
        Create a MemberInvoiceItem from a TowDataItem.

        Parameters
        ----------
        tow_data : TowDataItem
            The TowDataItem instance containing the tow data.

        Returns
        -------
        list[MemberInvoiceItem]
            0-2 MemberInvoiceItem's populated with data from the TowDataItem containing:
            - Item for Glider Rental if billable rental is True
            - Item for Towing if billable tow is True
        """
        items: list[MemberInvoiceItem] = list()

        if not tow_data.flown_flag:
            log.warning(
                f"Tow Data for ticket {tow_data.ticket} has not been flown. No invoice items will be created.")
            return items
        if tow_data.closed_flag:
            log.warning(
                f"Tow Data for ticket {tow_data.ticket} is closed. No invoice items will be created.")
            return items

        # Assuming last name is the first part of the pilot's name
        last_name, first_name = [x.strip() for x in tow_data.pilot.split(',')]

        if tow_data.billable_rental:
            item = cls(
                display_name=tow_data.pilot,
                # Set invoice_date to now, due_date to 30 days after invoice_date
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Glider: {tow_data.glider_id}, Glider Time: {tow_data.glider_time} hours',
                product=Product.GLIDER,
                classification=Classification.GLIDER,
                last_name=last_name,
                first_name=first_name,
                amount=tow_data.rental_fee
            )
            items.append(item)

        if tow_data.billable_tow:
            item = cls(
                display_name=tow_data.pilot,
                # Set invoice_date to now, due_date to 30 days after invoice_date
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}',
                product=Product.TOW,
                classification=Classification.TOW,
                last_name=last_name,
                first_name=first_name,
                amount=tow_data.tow_fee
            )
            items.append(item)

        return items


def save_member_invoice(filename: str, invoices: Iterator[MemberInvoiceItem]) -> None:
    """
    Save the billing data to a CSV file.

    Parameters
    ----------
    filename : str
        The path to the CSV file where the invoice data will be saved.
    items : Iterator[MemberInvoiceItem]
        An iterator of MemberInvoiceItem objects representing the invoice items to be saved.

    Returns
    -------
    None

    Notes
    -----
    This method writes the provided invoice items to a CSV file using the specified filename.
    """
    invoices_by_pilot: dict[str, list[MemberInvoiceItem]] = dict()
    for item in invoices:
        key = item.display_name
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

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for pilot, invoices in sorted(invoices_by_pilot.items()):
            for idx, item in enumerate(sorted(invoices, lambda x: x.service_date)):
                if idx == 0:
                    display_name = item.display_name
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
                    item.service_date.strftime('%m/%d/%Y'),
                    item.description,
                    item.product.value,
                    item.classification.value,
                    item.last_name,
                    item.first_name,
                    f"${item.amount:.2f}"
                ]
                writer.writerow(row)
