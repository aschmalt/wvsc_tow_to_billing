"""This module provides the class for handling TOW data and converting it."""
# pylint: disable=cyclic-import
from importlib.metadata import PackageNotFoundError, version

from .converter import (
    convert_tow_ticket_to_all_invoices,
    convert_tow_ticket_to_member_invoice,
    convert_tow_ticket_to_vendor_bill,
)
from .member_invoice import MemberInvoiceItem, export_member_invoices_to_csv
from .tow_data import TowDataItem
from .vendor_bill import VendorBillItem, export_vendor_bills_to_csv

__all__ = [
    "TowDataItem",
    "MemberInvoiceItem",
    "VendorBillItem",
    "export_member_invoices_to_csv",
    "export_vendor_bills_to_csv",
    "convert_tow_ticket_to_member_invoice",
    "convert_tow_ticket_to_vendor_bill",
    "convert_tow_ticket_to_all_invoices"
]

try:
    __version__ = version("tow-conversion")
except PackageNotFoundError:
    __version__ = "0.0.0"
