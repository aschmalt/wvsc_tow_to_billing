from pathlib import Path
import pytest
import filecmp
from tow_conversion import (TowDataItem,
                            MemberInvoice,
                            save_member_invoices_csv,
                            save_vendor_bill_csv)


@pytest.fixture
def sample_data_dir() -> Path:
    """Fixture to provide a sample directory path."""
    return Path(__file__).parents[1] / "sample_data"


def test_convert_member_invoice(sample_data_dir: Path, tmp_path: Path) -> None:
    input_file = sample_data_dir / 'tow_ticket_output.csv'
    golden_file = sample_data_dir / 'member_invoice.csv'
    all_tow_data = TowDataItem.read_from_tow_csv(input_file)
    member_invoice = [MemberInvoice.from_tow_data(x) for x in all_tow_data]

    output_file = tmp_path / 'member_invoice.csv'
    save_member_invoices_csv(member_invoice, output_file)

    assert filecmp.cmp(golden_file, output_file, shallow=False), \
        f"Output file {output_file} does not match the golden file {golden_file}."
