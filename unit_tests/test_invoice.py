import pytest
from datetime import datetime
from enum import Enum
from unittest.mock import MagicMock, patch
from tow_conversion.invoice import Invoice
from tow_conversion.name import Name

# Dummy Enum for testing


class DummyCategory(Enum):
    FOO = 1
    BAR = 2


class DummyClassification(Enum):
    A = 1
    B = 2


class DummyProduct(Enum):
    X = 1
    Y = 2


@pytest.fixture
def valid_invoice_kwargs():
    return {
        "name": "John Doe",
        "invoice_date": datetime(2024, 1, 1),
        "due_date": datetime(2024, 1, 10),
        "service_date": datetime(2024, 1, 2),
        "description": "Test service",
        "amount": 100.0,
        "category": DummyCategory.FOO,
        "classification": DummyClassification.A,
        "product": DummyProduct.X,
    }


def test_invoice_init_with_str_name(valid_invoice_kwargs):
    invoice = Invoice(**valid_invoice_kwargs)
    assert isinstance(invoice.name, Name)
    assert invoice.name == "John Doe"
    assert invoice.amount == 100.0


def test_invoice_init_with_name_instance(valid_invoice_kwargs):
    valid_invoice_kwargs["name"] = Name("Jane Doe")
    invoice = Invoice(**valid_invoice_kwargs)
    assert isinstance(invoice.name, Name)
    assert invoice.name == "Jane Doe"


def test_invoice_negative_amount_raises(valid_invoice_kwargs):
    valid_invoice_kwargs["amount"] = -5.0
    with pytest.raises(ValueError):
        Invoice(**valid_invoice_kwargs)


def test_invoice_optional_enums_none(valid_invoice_kwargs):
    valid_invoice_kwargs["category"] = None
    valid_invoice_kwargs["classification"] = None
    valid_invoice_kwargs["product"] = None
    invoice = Invoice(**valid_invoice_kwargs)
    assert invoice.category is None
    assert invoice.classification is None
    assert invoice.product is None


def test_is_tow_ticket_completed_true():
    tow_data = MagicMock()
    tow_data.flown_flag = True
    tow_data.closed_flag = True
    tow_data.ticket = "T123"
    assert Invoice.is_tow_ticket_completed(tow_data) is True


def test_is_tow_ticket_completed_not_flown_logs_warning():
    tow_data = MagicMock()
    tow_data.flown_flag = False
    tow_data.closed_flag = True
    tow_data.ticket = "T124"
    with patch("tow_conversion.invoice.log") as mock_log:
        assert Invoice.is_tow_ticket_completed(tow_data) is False
        mock_log.warning.assert_called_once()
        assert "has not been flown" in mock_log.warning.call_args[0][0]


def test_is_tow_ticket_completed_not_closed_logs_warning():
    tow_data = MagicMock()
    tow_data.flown_flag = True
    tow_data.closed_flag = False
    tow_data.ticket = "T125"
    with patch("tow_conversion.invoice.log") as mock_log:
        assert Invoice.is_tow_ticket_completed(tow_data) is False
        mock_log.warning.assert_called_once()
        assert "is not closed" in mock_log.warning.call_args[0][0]


def test_is_tow_ticket_completed_no_logging_when_disabled():
    tow_data = MagicMock()
    tow_data.flown_flag = False
    tow_data.closed_flag = False
    tow_data.ticket = "T126"
    with patch("tow_conversion.invoice.log") as mock_log:
        assert Invoice.is_tow_ticket_completed(
            tow_data, log_warnings=False) is False
        mock_log.warning.assert_not_called()
