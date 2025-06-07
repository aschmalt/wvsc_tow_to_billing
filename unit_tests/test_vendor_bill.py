from pathlib import Path
import pytest
import csv
from datetime import datetime, timedelta

from tow_conversion import TowDataItem
from tow_conversion.vendor_bill import (
    VendorBillItem,
    Category,
    Classification,
    export_vendor_bills_to_csv
)


def create_dummy_tow_data_item(**kwargs) -> TowDataItem:
    """Create a dummy TowDataItem with default values, allowing for overrides."""
    settings = {'flown_flag': True,
                'closed_flag': True,
                'pilot': "Smith, John",
                'ticket': "123",
                'tow_pilot': "Doe, Jane",
                'tow_plane': "Cessna 172",
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
                'category': 'Club Flight',
                'guest': 'my Guest', }
    settings.update(kwargs)
    return TowDataItem(**settings)


def test_vendor_bill_item_positive_amount() -> None:
    item = VendorBillItem(
        name="Last, First",
        invoice_date=datetime.now(),
        due_date=datetime.now(),
        service_date=datetime.now(),
        description="Test memo",
        category=Category.TOW,
        classification=Classification.TOW,
        amount=100.0
    )
    assert item.amount == 100.0


def test_vendor_bill_item_negative_amount_raises() -> None:
    with pytest.raises(ValueError):
        VendorBillItem(
            name="Vendor",
            invoice_date=datetime.now(),
            due_date=datetime.now(),
            service_date=datetime.now(),
            description="Test memo",
            category=Category.TOW,
            classification=Classification.TOW,
            amount=-1.0
        )


def test_from_tow_data_returns_empty_if_not_flown() -> None:
    tow_data = create_dummy_tow_data_item(flown_flag=False)
    items = VendorBillItem.from_tow_data(tow_data)
    assert items == list()


def test_from_tow_data_returns_empty_if_not_closed() -> None:
    tow_data = create_dummy_tow_data_item(closed_flag=False)
    items = VendorBillItem.from_tow_data(tow_data)
    assert items == list()


def test_from_tow_data_returns_tow_and_intro_items() -> None:
    tow_data = create_dummy_tow_data_item(category="Intro")
    items = VendorBillItem.from_tow_data(tow_data)
    assert len(items) == 2
    item1, item2 = items
    assert item1.category == Category.TOW
    assert str(item1.name) == 'Doe, Jane'
    assert item1.amount == 10.00
    assert item1.service_date == tow_data.date_time
    assert item1.classification == Classification.TOW
    assert item1.description == 'Ticket #: 123, Release Alt: 3000, Cessna 172 Pilot: Smith, John'

    assert item2.category == Category.INTRO
    assert str(item2.name) == tow_data.pilot
    assert item2.amount == 10.00
    assert item2.service_date == tow_data.date_time
    assert item2.classification == Classification.INTRO
    assert item2.description == 'Ticket #: 123, Release Alt: 3000 Glider: G1, my Guest'


def test_from_tow_data_returns_only_tow_if_not_intro() -> None:
    tow_data = create_dummy_tow_data_item(category="Club Flight")
    items = VendorBillItem.from_tow_data(tow_data)
    assert len(items) == 1
    item = items[0]
    assert item.category == Category.TOW
    assert str(item.name) == 'Doe, Jane'
    assert item.amount == 10.00
    assert item.service_date == tow_data.date_time
    assert item.classification == Classification.TOW
    assert item.description == 'Ticket #: 123, Release Alt: 3000, Cessna 172 Pilot: Smith, John'


def test_export_vendor_bills_to_csv_creates_file_and_content(tmp_path: Path) -> None:
    # Prepare items
    now = datetime(2008, 6, 18, 11, 23, 34)
    item1 = VendorBillItem(
        invoice_date=now,
        due_date=now + timedelta(days=30),
        service_date=now,
        description="Memo1",
        category=Category.TOW,
        classification=Classification.TOW,
        name="VendorA",
        amount=50.0
    )
    item2 = VendorBillItem(
        invoice_date=now,
        due_date=now + timedelta(days=30),
        service_date=now + timedelta(days=1),
        description="Memo2",
        category=Category.INTRO,
        classification=Classification.INTRO,
        name="VendorA",
        amount=75.0
    )
    item3 = VendorBillItem(
        invoice_date=now,
        due_date=now + timedelta(days=30),
        service_date=now,
        description="Memo3",
        category=Category.TOW,
        classification=Classification.TOW,
        name="VendorB",
        amount=100.0
    )
    filename = tmp_path / "test_vendor_bills.csv"
    export_vendor_bills_to_csv(filename, iter([item1, item2, item3]))

    # Read back and check
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0][0] == "Vendor Name"
    assert rows[1][0] == "VendorA."
    assert rows[2][0] == ""
    assert rows[3][0] == "VendorB."
    assert rows[1][-2] == "VendorA"
    assert rows[2][-2] == "VendorA"
    assert rows[3][-2] == "VendorB"
    assert rows[1][-1] == "$50.00"
    assert rows[2][-1] == "$75.00"
    assert rows[3][-1] == "$100.00"
    assert rows[1][3] == "06/18/2008 11:23"  # Check date format


def test_export_vendor_bills_to_csv_accepts_path_object(tmp_path: Path) -> None:
    now = datetime(2024, 1, 1)
    item = VendorBillItem(
        invoice_date=now,
        due_date=now + timedelta(days=30),
        service_date=now,
        description="Memo",
        category=Category.TOW,
        classification=Classification.TOW,
        name="Vendor",
        amount=10.0
    )
    filename = tmp_path / "test_path_obj.csv"
    export_vendor_bills_to_csv(filename, iter([item]))
    assert filename.exists()
    with open(filename) as f:
        content = f.read()
    assert "Vendor" in content
    assert "$10.00" in content
