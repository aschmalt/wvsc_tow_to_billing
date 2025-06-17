"""Module to define the VendorBillItem class for tow & intro billing information and method to save"""
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import logging
import csv
from tow_conversion.tow_data import TowDataItem, TicketCategory
from tow_conversion.invoice import Invoice
from tow_conversion.name import Name

log = logging.getLogger('VendorBill')


class Classification(Enum):
    """Class to hold classification constants for the MemberInvoiceItem."""
    INTRO = "INTRO RIDES"
    TOW = "TOW"
    PACK = "5 PACKS"


class Category(Enum):
    """Class to hold category constants for the MemberInvoiceItem."""
    INTRO = "Intro Pilot Expense"
    TOW = "Tow Pilot Expense"
    PACK = "5 Pack Expense"


COSTS = {
    Classification.INTRO: 10.00,
    Classification.TOW: 10.00,
    Classification.PACK: 40.00
}


class VendorBillItem(Invoice):
    """Class to hold vendor bill data for a tow."""

    @classmethod
    def from_tow_data(cls, tow_data: TowDataItem, log_unbillable_tow_tickets: bool = True) -> list['VendorBillItem']:
        """
        Create a VendorBillItem from a TowDataItem.

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
        list[VendorBillItem]
            A list of VendorBillItem instances created from the provided TowDataItem.
        """
        items: list[VendorBillItem] = list()
        if not cls.is_tow_ticket_completed(tow_data, log_warnings=log_unbillable_tow_tickets):
            return items

        if tow_data.tow_pilot:
            # Tow Pilot Expense when not self-launched
            tow_bill = VendorBillItem(
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}, {tow_data.tow_plane}, Pilot: {tow_data.pilot}',  # pylint: disable=line-too-long
                category=Category.TOW,
                classification=Classification.TOW,
                name=tow_data.tow_pilot,
                amount=COSTS[Classification.TOW]
            )
            items.append(tow_bill)

        # Intro Pilot Expense
        if tow_data.category == TicketCategory.INTRO:
            intro_bill = VendorBillItem(
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}, Glider: {tow_data.glider_id}, {tow_data.guest}',  # pylint: disable=line-too-long
                category=Category.INTRO,
                classification=Classification.INTRO,
                name=tow_data.pilot,
                amount=COSTS[Classification.INTRO]
            )
            items.append(intro_bill)

        # 5 Packs
        if tow_data.category == TicketCategory.PACK:
            if not tow_data.cfig:
                log.error(
                    'Tow ticket %s is a PACK but has no CFIG. Skipping.', tow_data.ticket)
                return items
            pack_bill = VendorBillItem(
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_date=tow_data.date_time,
                description=f'Ticket #: {tow_data.ticket}, Release Alt: {tow_data.release_alt}, Glider: {tow_data.glider_id}, {tow_data.pilot}',  # pylint: disable=line-too-long
                category=Category.PACK,
                classification=Classification.PACK,
                name=tow_data.cfig,
                amount=COSTS[Classification.PACK]
            )
            items.append(pack_bill)

        return items


def export_vendor_bills_to_csv(filename: str | Path, invoices: list[VendorBillItem]) -> None:
    """
    Save the vendor bill data to a CSV file.

    Parameters
    ----------
    filename : str or Path
        The path to the CSV file where the vendor bill data will be saved.
    items : list[VendorBillItem]
        An list of VendorBillItem objects representing the items to be saved.

    Returns
    -------
    None

    Notes
    -----
    This method writes the provided vendor bill items to the specified CSV file.
    """
    invoices_by_vendor: dict[Name, list[VendorBillItem]] = dict()
    for item in invoices:
        key = item.name
        # Group items by vendor name (pilot)
        if key not in invoices_by_vendor:
            invoices_by_vendor[key] = list()
        invoices_by_vendor[key].append(item)

    headers = ['Vendor Name',
               'Bill Date',
               'Due Date2',
               'Service Date',
               'Category Details - Memo',
               'Category Details - Category',
               'CLASS',
               'SORT NAME',
               'Sum of Category Details - Amount']

    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for pilot, pilot_invoices in sorted(invoices_by_vendor.items()):
            for idx, item in enumerate(sorted(pilot_invoices, key=lambda x: x.service_date)):
                if idx == 0:
                    vendor_name = f'{pilot}.'
                    invoice_date = item.invoice_date.strftime('%m/%d/%Y')
                    due_date = item.due_date.strftime('%m/%d/%Y')
                else:
                    vendor_name = ''
                    invoice_date = ''
                    due_date = ''
                row = [
                    vendor_name,
                    invoice_date,
                    due_date,
                    item.service_date.strftime('%m/%d/%Y %H:%M'),
                    item.description,
                    item.category.value,
                    item.classification.value,
                    item.name,
                    f"${item.amount:.2f}"
                ]
                writer.writerow(row)
