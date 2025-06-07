from pathlib import Path
import csv
from datetime import datetime, timedelta
import pytest

from tow_conversion import TowDataItem
from tow_conversion.member_invoice import (
    MemberInvoiceItem,
    Product,
    Classification,
    export_member_invoices_to_csv,
)


def create_dummy_tow_data_item(**kwargs) -> TowDataItem:
    """Create a dummy TowDataItem with default values, allowing for overrides."""
    settings = {'flown_flag': True,
                'closed_flag': True,
                'pilot': "Smith, John",
                'ticket': "123",
                'glider_id': "G1",
                'glider_time': 1.5,
                'billable_rental': True,
                'billable_tow': True,
                'rental_fee': 50.0,
                'tow_fee': 75.0,
                'release_alt': 3000,
                'tow_speed': 60,
                'date_time': datetime(2024, 6, 1),
                'tow_type': 'Areo',
                'airport': '10R4',
                'category': 'Club Flight'}
    settings.update(kwargs)
    return TowDataItem(**settings)


def test_member_invoice_item_post_init_negative_amount() -> None:
    with pytest.raises(ValueError):
        MemberInvoiceItem(
            name="Smith, John",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            service_date=datetime.now(),
            description="desc",
            product=Product.TOW,
            classification=Classification.TOW,
            amount=-1.0,
        )


def test_member_invoice_item_from_tow_data_both_items() -> None:
    tow_data = create_dummy_tow_data_item()
    items = MemberInvoiceItem.from_tow_data(tow_data)
    assert len(items) == 2
    assert any(i.product == Product.GLIDER for i in items)
    assert any(i.product == Product.TOW for i in items)
    assert all(i.name.last == "Smith" and
               i.name.first == "John" for i in items)


def test_member_invoice_item_from_tow_data_only_tow() -> None:
    tow_data = create_dummy_tow_data_item(
        billable_rental=False, billable_tow=True)
    items = MemberInvoiceItem.from_tow_data(tow_data)
    assert len(items) == 1
    assert items[0].product == Product.TOW


def test_member_invoice_item_from_tow_data_only_rental() -> None:
    tow_data = create_dummy_tow_data_item(
        billable_rental=True, billable_tow=False)
    items = MemberInvoiceItem.from_tow_data(tow_data)
    assert len(items) == 1
    assert items[0].product == Product.GLIDER


def test_member_invoice_item_from_tow_data_not_flown() -> None:
    tow_data = create_dummy_tow_data_item(flown_flag=False)
    items = MemberInvoiceItem.from_tow_data(tow_data)
    assert items == list()


def test_member_invoice_item_from_tow_data_not_closed() -> None:
    tow_data = create_dummy_tow_data_item(closed_flag=False)
    items = MemberInvoiceItem.from_tow_data(tow_data)
    assert items == list()


def test_save_member_invoice_creates_csv(tmp_path: Path) -> None:
    # Prepare two pilots, each with one invoice
    now = datetime(2024, 6, 1, 17, 23, 34)
    items = [
        MemberInvoiceItem(
            name="Smith, John",
            invoice_date=now,
            due_date=now + timedelta(days=30),
            service_date=now,
            description="desc1",
            product=Product.TOW,
            classification=Classification.TOW,
            amount=100.0,
        ),
        MemberInvoiceItem(
            name="Doe, Jane",
            invoice_date=now,
            due_date=now + timedelta(days=30),
            service_date=now,
            description="desc2",
            product=Product.GLIDER,
            classification=Classification.GLIDER,
            amount=50.0,
        ),
    ]
    csv_file_output = tmp_path / "test_invoice.csv"
    export_member_invoices_to_csv(str(csv_file_output), items)
    with open(csv_file_output, newline='') as f:
        reader = list(csv.reader(f))
    assert reader[0] == [
        'Display Name',
        'Invoice Date',
        'Due Date',
        'Service Date',
        'Description or Memo',
        'Product',
        'CLASS',
        'SORT Last Name',
        'SORT First Name',
        'Sum of Tow Fee'
    ]
    assert any("Smith, John" in row for row in reader)
    assert any("Doe, Jane" in row for row in reader)
    assert any("$100.00" in row for row in reader)
    assert any("$50.00" in row for row in reader)
    assert reader[1][3] == now.strftime('06/01/2024 17:23')


def test_save_member_invoice_groups_by_display_name(tmp_path) -> None:
    now = datetime(2024, 6, 1)
    items = [
        MemberInvoiceItem(
            name="Smith, John",
            invoice_date=now,
            due_date=now + timedelta(days=30),
            service_date=now,
            description="desc1",
            product=Product.TOW,
            classification=Classification.TOW,
            amount=100.0,
        ),
        MemberInvoiceItem(
            name="Smith, John",
            invoice_date=now,
            due_date=now + timedelta(days=30),
            service_date=now + timedelta(days=1),
            description="desc2",
            product=Product.GLIDER,
            classification=Classification.GLIDER,
            amount=50.0,
        ),
    ]

    filename = tmp_path / "test_invoice_group.csv"
    export_member_invoices_to_csv(str(filename), iter(items))
    with open(filename, newline='') as f:
        rows = list(csv.reader(f))
    # The first row for Smith, John should have display name, invoice date, due date
    smith_rows = [row for row in rows if row[0] == "Smith, John"]
    assert len(smith_rows) == 1
    # The second row for Smith, John should have empty display name, invoice date, due date
    empty_rows = [row for row in rows if row[0] == "" and row[7] == "Smith"]
    assert len(empty_rows) == 1
