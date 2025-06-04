import pytest
from tow_conversion import TowDataItem
from datetime import datetime
from tow_conversion.tow_data import TowDataItem


def valid_tow_kwargs() -> dict[str, int | datetime | str | float]:
    return dict(
        ticket=1,
        date_time=datetime(2024, 6, 1, 12, 0),
        pilot="John Doe",
        airport="WVSC",
        category="Instruction",
        glider_id="G-123",
        tow_type="Aerotow",
        flight_brief="Standard",
        cfig="Jane Smith",
        guest="Guest Name",
        billable_rental=True,
        billable_tow=True,
        tow_speed=60,
        alt_required=2000,
        release_alt=2000,
        glider_time=1.0,
        tow_fee=50.0,
        rental_fee=30.0,
        remarks="No remarks",
        certificate="CERT123",
        tow_pilot="Tow Pilot",
        tow_plane="Tow Plane",
        flown_flag=True,
        closed_flag=True
    )


def test_valid_towdata_creation() -> None:
    tow = TowDataItem(**valid_tow_kwargs())
    assert tow.ticket == 1
    assert tow.pilot == "John Doe"
    assert tow.tow_fee == 50.0
    assert tow.rental_fee == 30.0
    assert tow.flown_flag is True
    assert tow.closed_flag is True


def test_ticket_must_be_non_negative() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['ticket'] = ''
    with pytest.raises(ValueError, match="Tow Ticket must have a value."):
        TowDataItem(**kwargs)


def test_rental_fee_must_be_positive_if_billable() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['rental_fee'] = 0
    with pytest.raises(ValueError, match="Rental fee must be greater than 0, if billable rental is True."):
        TowDataItem(**kwargs)


def test_tow_fee_must_be_positive_if_billable() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['tow_fee'] = 0
    with pytest.raises(ValueError, match="Tow fee must be greater than 0, if billable tow is True."):
        TowDataItem(**kwargs)


def test_glider_time_must_be_positive_if_billable() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['glider_time'] = 0
    with pytest.raises(ValueError, match="Glider time must be greater than 0, if billable rental is True."):
        TowDataItem(**kwargs)


def test_release_alt_must_be_positive() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['release_alt'] = 0
    with pytest.raises(ValueError, match="Release altitude must be greater than 0."):
        TowDataItem(**kwargs)


def test_tow_speed_must_be_positive() -> None:
    kwargs = valid_tow_kwargs()
    kwargs['tow_speed'] = 0
    with pytest.raises(ValueError, match="Tow speed must be greater than 0."):
        TowDataItem(**kwargs)


def test_str_and_repr_methods() -> None:
    tow = TowDataItem(**valid_tow_kwargs())
    s = str(tow)
    r = repr(tow)
    assert "TOW Ticket: 1" in s
    assert "TowDataItem(ticket=1)" in r


def test_read_from_tow_csv(tmp_path) -> None:
    """Test reading from a CSV file."""
    import csv
    tow_data = valid_tow_kwargs()

    csv_data = {
        'Ticket #': tow_data['ticket'],
        'Date Time': tow_data['date_time'].strftime('%Y-%m-%d %H:%M:%S'),
        'Bill To/Pilot': tow_data['pilot'],
        'Month': tow_data['date_time'].strftime('%m'),
        'CFIG': tow_data['cfig'],
        'Guest': tow_data['guest'],
        'Airport': tow_data['airport'],
        'Category': tow_data['category'],
        'Billable Rental': '1' if tow_data['billable_rental'] else '0',
        'Billable Tow': '1' if tow_data['billable_tow'] else '0',
        'Glider ID': tow_data['glider_id'],
        'Tow Type': tow_data['tow_type'],
        'Tow Speed': tow_data['tow_speed'],
        'Alt Required': tow_data['alt_required'],
        'Release Alt': tow_data['release_alt'],
        'Glider Time': tow_data['glider_time'],
        'Tow Raw': tow_data['tow_fee'],
        'Tow Fee': tow_data['tow_fee'],
        'Rental Raw': tow_data['rental_fee'],
        'Glider Rental': tow_data['rental_fee'],
        'Flight Brief': tow_data['flight_brief'],
        'Remarks': tow_data['remarks'],
        'Certificate': tow_data['certificate'],
        'Tow Pilot': tow_data['tow_pilot'],
        'Tow Plane': tow_data['tow_plane'],
        'Flown Flag': '1' if tow_data['flown_flag'] else '0',
        'Closed Flag': '1' if tow_data['closed_flag'] else '0'
    }

    csv_file = tmp_path / "tow_data.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_data.keys())
        writer.writeheader()
        writer.writerow(csv_data)

    all_data = list(TowDataItem.read_from_tow_csv(csv_file))
    assert len(all_data) == 1
    tow_instance = all_data[0]
    assert isinstance(tow_instance, TowDataItem)
    for key, value in tow_data.items():
        got = getattr(tow_instance, key)
        assert got == value, f"Expected {key} to be {value}, got {got}"
