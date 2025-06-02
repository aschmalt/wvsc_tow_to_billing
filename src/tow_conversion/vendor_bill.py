from collections.abc import Iterator
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import csv
from tow_conversion import TowDataItem

log = logging.getLogger('VendorBill')


class Classification(Enum):
    """Class to hold classification constants for the MemberInvoiceItem."""
    INTRO = "INTRO RIDES"
    TOW = "TOW"


class Category(Enum):
    """Class to hold category constants for the MemberInvoiceItem."""
    INTRO = "Intro Pilot Expense"
    TOW = "Tow Pilot Expense"


@dataclass
class VendorBillItem:
    """Class to hold vendor bill data for a tow."""
    vendor_name: str = field(
        metadata={"description": "Name of the vendor"})
    bill_date: datetime = field(
        metadata={"description": "Date of the invoice in '%m/%d/%Y' format"})
    due_date: datetime = field(
        metadata={"description": "Due date for the invoice in '%m/%d/%Y' format"})
    service_date: datetime = field(
        metadata={"description": "Date of service in '%m/%d/%Y' format"})
    memo: str = field(
        metadata={"description": "Memo or notes for the bill"})
    category: Category = field(
        metadata={"description": "Category of the service"})
    classification: Classification = field(
        metadata={"description": "Classification of the service"})
    name: str = field(
        metadata={"description": "Name of the person or entity for bill"})
    amount: float = field(default=10.00,
                          metadata={"description": "Amount charged for the service in dollars"})

    def __post_init__(self) -> None:
        """Post-initialization validation for the VendorBill class."""
        if self.amount < 0:
            raise ValueError("Amount must be a non-negative value.")

    @classmethod
    def from_tow_data(cls, tow_data: TowDataItem) -> list['VendorBillItem']:
        """
        Create a VendorBillItem from a TowDataItem.

        Parameters
        ----------
        tow_data : TowDataItem
            The TowDataItem instance containing the tow data.

        Returns
        -------
        list[VendorBillItem]
            A list of VendorBillItem instances created from the provided TowDataItem.
        """
        items: list[VendorBillItem] = list()

        if not tow_data.flown_flag:
            log.warning(
                f"Tow Data for ticket {tow_data.ticket} has not been flown. No invoice items will be created.")
            return items
        if tow_data.closed_flag:
            log.warning(
                f"Tow Data for ticket {tow_data.ticket} is closed. No invoice items will be created.")
            return items

        # Tow Pilot Expense
        tow_bill = VendorBillItem(
            vendor_name=tow_data.tow_pilot,
            bill_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            service_date=tow_data.date_time,
            memo=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}, {tow_data.tow_plane} Pilot: {tow_data.pilot}',
            category=Category.TOW,
            classification=Classification.TOW,
            name=tow_data.tow_pilot,
        )
        items.append(tow_bill)

        # Intro Pilot Expense
        if tow_data.category.lower() == 'intro':
            intro_bill = VendorBillItem(
                vendor_name=tow_data.pilot,
                bill_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                memo=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}, Glider: {tow_data.glider_id}, {tow_data.guest}',
                category=Category.INTRO,
                classification=Classification.INTRO,
                name=tow_data.pilot,
            )
            items.append(intro_bill)

        # TODO: How are 5 Packs handled?

        return items


def save_vendor_bill(filename: str | Path, items: Iterator[VendorBillItem]) -> None:
    """
    Save the vendor bill data to a CSV file.

    Parameters
    ----------
    filename : str or Path
        The path to the CSV file where the vendor bill data will be saved.
    items : Iterator[VendorBillItem]
        An iterator of VendorBillItem objects representing the items to be saved.

    Returns
    -------
    None

    Notes
    -----
    This method writes the provided vendor bill items to the specified CSV file.
    """
