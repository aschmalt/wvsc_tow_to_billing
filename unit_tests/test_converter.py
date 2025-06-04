from pathlib import Path
import pytest
import csv
from tow_conversion import (convert_tow_ticket_to_member_invoice,
                            convert_tow_ticket_to_vendor_bill)


@pytest.fixture
def sample_data_dir() -> Path:
    """Fixture to provide a sample directory path."""
    return Path(__file__).parents[1] / "sample_data"


def test_convert_member_invoice(sample_data_dir: Path, tmp_path: Path) -> None:
    input_file = sample_data_dir / 'tow_ticket_output.csv'
    assert input_file.exists(), \
        f"Input file {input_file} does not exist."
    golden_file = sample_data_dir / 'member_invoice.csv'
    assert golden_file.exists(), \
        f"Golden file {golden_file} does not exist."

    output_file = tmp_path / 'test_output.csv'
    convert_tow_ticket_to_member_invoice(tow_ticket_file=input_file,
                                         output_file=output_file)

    with open(output_file, 'r', encoding='utf-8') as output_f:
        output_data = list(csv.DictReader(output_f))

    with open(golden_file, 'r', encoding='utf-8-sig') as golden_f:
        golden_data = list(csv.DictReader(golden_f))

    assert len(output_data) == len(golden_data), \
        f"Output file {output_file} has {len(output_data)} rows, expected {len(golden_data)} rows."
    golden_keys = [x.strip() for x in golden_data[0].keys()]
    output_keys = [x.strip() for x in output_data[0].keys()]
    assert output_keys == golden_keys, \
        f"Output file has different headers than the golden file."
    for output_row, golden_row in zip(output_data, golden_data):
        for key in ['Display Name',
                    # 'Invoice Date',
                    # 'Due Date',
                    'Service Date',
                    'Description or Memo',
                    'Product',
                    'CLASS',
                    'SORT Last Name',
                    'SORT First Name',
                    'Sum of Tow Fee']:
            assert output_row[key].strip() == golden_row[key].strip(), \
                f"{key} mismatch in output file and golden file for row {output_row}"


def test_convert_vendor_bills(sample_data_dir: Path, tmp_path: Path) -> None:
    input_file = sample_data_dir / 'tow_ticket_output.csv'
    assert input_file.exists(), \
        f"Input file {input_file} does not exist."
    golden_file = sample_data_dir / 'vendor_bill.csv'
    assert golden_file.exists(), \
        f"Golden file {golden_file} does not exist."

    output_file = tmp_path / 'test_output.csv'
    convert_tow_ticket_to_vendor_bill(tow_ticket_file=input_file,
                                      output_file=output_file)

    with open(output_file, 'r', encoding='utf-8') as output_f:
        output_data = list(csv.DictReader(output_f))

    with open(golden_file, 'r', encoding='utf-8-sig') as golden_f:
        golden_data = list(csv.DictReader(golden_f))

    assert len(output_data) == len(golden_data), \
        f"Output file {output_file} has {len(output_data)} rows, expected {len(golden_data)} rows."
    golden_keys = [x.strip() for x in golden_data[0].keys()]
    output_keys = [x.strip() for x in output_data[0].keys()]
    assert output_keys == golden_keys, \
        f"Output file has different headers than the golden file."
    for output_row, golden_row in zip(output_data, golden_data):
        for key in ['Vendor Name',
                    # 'Bill Date',
                    # 'Due Date2',
                    'Service Date',
                    'Category Details - Memo',
                    'Category Details - Category',
                    'CLASS', 'SORT NAME',
                    'Sum of Category Details - Amount']:
            assert output_row[key].strip() == golden_row[key].strip(), \
                f"{key} mismatch in output file and golden file in row {output_row}"
