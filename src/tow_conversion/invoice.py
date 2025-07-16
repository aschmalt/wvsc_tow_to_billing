"""Base invoice class for the invoice modules."""
from abc import ABC
import logging
from datetime import datetime
from enum import Enum
from tow_conversion.tow_data import TowDataItem, TicketCategory
from tow_conversion.name import Name

log = logging.getLogger('Invoice')


class Invoice(ABC):
    """Base class for invoice items, providing common attributes and methods."""
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments

    def __init__(
        self,
        name: Name | str,
        invoice_date: datetime,
        due_date: datetime,
        service_date: datetime,
        description: str,
        amount: float,
        category: Enum | None = None,
        classification: Enum | None = None,
        product: Enum | None = None,
    ) -> None:
        """
        Base invoice class.

        Parameters
        ----------
        name : Name or str
            Name for the invoice item, typically the vendor or member.
        invoice_date : datetime
            Date of the invoice in '%m/%d/%Y' format.
        due_date : datetime
            Due date for the invoice in '%m/%d/%Y' format.
        service_date : datetime
            Date of service in '%m/%d/%Y' format.
        description : str
            Memo or notes for the bill.
        amount : float
            Amount charged for the service in dollars.
        category : Enum | None
            Optional
            Category of the service, if applicable.
        classification : Enum | None
            Optional
            Classification of the service, if applicable.
        product : Enum | None
            Optional
            Product type for the service, if applicable.
        """
        if isinstance(name, str):
            name = Name(name)
        if amount < 0:
            raise ValueError("Amount must be a non-negative value.")

        self._name = name
        self.invoice_date = invoice_date
        self.due_date = due_date
        self.service_date = service_date
        self.description = description
        self.category = category
        self.classification = classification
        self.product = product
        self.amount = amount

    @property
    def name(self) -> Name:
        """Get the name of the invoice item."""
        return self._name

    @staticmethod
    def is_tow_ticket_completed(tow_data: TowDataItem, log_warnings: bool = True) -> bool:
        """
        Checks whether a tow ticket is completed based on flown and closed flags.
        Parameters
        ----------
        tow_data : TowDataItem
            The tow data item containing ticket information and status flags.
        log_warnings : bool, optional
            If False, suppresses warning logs for unflown or unclosed tickets.
            Defaults to True, which will log warnings if the ticket is not completed.
        Returns
        -------
        bool
            True if the tow ticket has been both flown and closed, False otherwise.
        """

        if not tow_data.flown_flag:
            if log_warnings:
                log.warning(
                    "Tow Data for ticket %s has not been flown. No invoice items will be created.", tow_data.ticket)
            return False
        if not tow_data.closed_flag and tow_data.category != TicketCategory.PRIVATE:
            if log_warnings:
                log.warning(
                    "Tow Data for ticket %s is not closed. No invoice items will be created.", tow_data.ticket)
            return False
        return True
