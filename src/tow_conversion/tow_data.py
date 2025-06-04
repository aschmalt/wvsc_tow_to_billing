"""Tow Data Item Class for Tow Ticket System CSV Import"""
from collections.abc import Generator
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import csv

# from enum import Enum
# class TowType(Enum):
#     """
#     Enum to represent different types of tows.
#     """
#     AEROTOW = "Aero"
#     WINCH = "Winch"
#     BLUEBIRD = "Bluebird"
#     UHAUL = "Uhaul"
#     OTHER = "Other"

# class FlightBrief(Enum):
#     """
#     Enum to represent flight brief types.
#     """
#     STANDARD = "Standard"
#     BOX_THE_WAKE = "Box the Wake"
#     ROPE_BREAK = "Rope Break"
#     PTT = "Premature Tow Termination"
#     EMERGENCY = "Emergency Breakaway"
#     SLACK_ROPE = "Slack Rope"
#     SINGALS = "Signals"
#     OTHER = "Other"


@dataclass
class TowDataItem:
    """Class to hold TOW data from Tow Ticket System."""
    ticket: str = field(
        metadata={"description": "Unique identifier for the tow ticket"})
    date_time: datetime = field(
        metadata={"description": "Date and time of the tow ticket in ISO 8601 format"})
    pilot: str = field(
        metadata={"description": "Name of the pilot or bill to"})
    airport: str = field(metadata={"description": "Airport code"})
    category: str = field(metadata={"description": "Category of the tow"})
    glider_id: str = field(metadata={"description": "ID of the glider used"})
    tow_type: str = field(
        metadata={"description": "Type of tow (e.g., aerotow, winch tow)"})
    # Optional fields
    flight_brief: str = field(default="Standard", metadata={
                              "description": "Flight brief type"})
    cfig: str = field(default="", metadata={
                      "description": "CFIG (Certified Flight Instructor) name, if applicable"})
    guest: str = field(default="", metadata={
                       "description": "Guest name, if applicable"})
    billable_rental: bool = field(default=True, metadata={
                                  "description": "Flag indicating if the tow is billable for rental"})
    billable_tow: bool = field(default=True, metadata={
                               "description": "Flag indicating if the tow is billable"})
    tow_speed: int = field(default=0, metadata={
                           "description": "Speed of the tow in knots"})
    alt_required: int = field(default=0, metadata={
                              "description": "Altitude Requested in feet"})
    release_alt: int = field(default=0, metadata={
                             "description": "Release altitude in feet"})
    glider_time: float = field(default=0.1, metadata={
                               "description": "Glider flight time in hours"})
    tow_fee: float = field(default=0.0, metadata={
                           "description": "Raw tow cost in dollars"})
    rental_fee: float = field(default=0.0, metadata={
                              "description": "Raw rental cost in dollars"})
    remarks: str = field(default="", metadata={
                         "description": "Remarks or notes about the tow"})
    certificate: str = field(default="", metadata={
                             "description": "Gift certificate information, if applicable"})
    tow_pilot: str = field(default="", metadata={
                           "description": "Name of the tow pilot"})
    tow_plane: str = field(default="", metadata={
                           "description": "Tow plane used"})
    flown_flag: bool = field(default=False, metadata={
                             "description": "Flag indicating if the tow was flown"})
    closed_flag: bool = field(default=False, metadata={
                              "description": "Flag indicating if the tow ticket is closed"})

    def __post_init__(self) -> None:
        """Post-initialization validation for the TowData class."""
        if not self.ticket:
            raise ValueError("Tow Ticket must have a value.")
        if self.billable_rental and self.rental_fee <= 0:
            raise ValueError(
                "Rental fee must be greater than 0, if billable rental is True.")
        if self.billable_tow and self.tow_fee <= 0:
            raise ValueError(
                "Tow fee must be greater than 0, if billable tow is True.")
        if self.billable_rental and self.glider_time <= 0:
            raise ValueError(
                "Glider time must be greater than 0, if billable rental is True.")
        if self.release_alt <= 0:
            raise ValueError("Release altitude must be greater than 0.")
        if self.tow_speed <= 0:
            raise ValueError("Tow speed must be greater than 0.")

    # pylint: disable=too-many-branches
    @classmethod
    def read_from_tow_csv(cls, file_path: str | Path) -> Generator['TowDataItem', str | Path, None]:
        """Read tow data from a CSV file and populate the instance."""
        with open(file_path, mode='r', encoding='ascii') as file:
            reader = csv.DictReader(file)
            for row in reader:
                inputs = {
                    'ticket': int(row['Ticket #']),
                    'date_time': datetime.fromisoformat(row['Date Time']),
                    'pilot': row['Bill To/Pilot'],
                    'airport': row['Airport'],
                    'category': row['Category'],
                    'glider_id': row['Glider ID'],
                    'tow_type': row['Tow Type'],
                }

                if row.get('Flight Brief', None):
                    inputs['flight_brief'] = row['Flight Brief']
                if row.get('CFIG', None):
                    inputs['cfig'] = row['CFIG']
                if row.get('Guest', None):
                    inputs['guest'] = row['Guest']
                if row.get('Billable Rental', None):
                    inputs['billable_rental'] = row['Billable Rental'] == '1'
                if row.get('Billable Tow', None):
                    inputs['billable_tow'] = row['Billable Tow'] == '1'
                if row.get('Tow Speed', None):
                    inputs['tow_speed'] = int(row['Tow Speed'])
                if row.get('Alt Required', None):
                    inputs['alt_required'] = int(row['Alt Required'])
                if row.get('Release Alt', None):
                    inputs['release_alt'] = int(row['Release Alt'])
                if row.get('Glider Time', None):
                    inputs['glider_time'] = float(row['Glider Time'])
                if row.get('Tow Fee', None):
                    inputs['tow_fee'] = float(row['Tow Fee'].lstrip('$'))
                if row.get('Glider Rental', None):
                    inputs['rental_fee'] = float(
                        row['Glider Rental'].lstrip('$'))
                if row.get('Remarks', None):
                    inputs['remarks'] = row['Remarks']
                if row.get('Certificate', None):
                    inputs['certificate'] = row['Certificate']
                if row.get('Tow Pilot', None):
                    inputs['tow_pilot'] = row['Tow Pilot']
                if row.get('Tow Plane', None):
                    inputs['tow_plane'] = row['Tow Plane']
                if row.get('Guest', None):
                    inputs['guest'] = row['Guest']
                if row.get('Flown Flag', None):
                    inputs['flown_flag'] = row.get('Flown Flag', None) == '1'
                if row.get('Closed Flag', None):
                    inputs['closed_flag'] = row.get('Closed Flag', None) == '1'

                yield cls(**inputs)

    def __str__(self) -> str:
        """String representation of the TowData instance."""
        return (f"TOW Ticket: {self.ticket}, Date/Time: {self.date_time.isoformat()}, "
                f"Pilot: {self.pilot}, Airport: {self.airport}, Category: {self.category}, "
                f"Glider ID: {self.glider_id}, Tow Type: {self.tow_type}, "
                f"Flight Brief: {self.flight_brief}, CFIG: {self.cfig}, Guest: {self.guest}, "
                f"Billable Rental: {self.billable_rental}, Billable Tow: {self.billable_tow}, "
                f"Tow Speed: {self.tow_speed} knots, Alt Required: {self.alt_required} feet, "
                f"Release Altitude: {self.release_alt} feet, Glider Time: {self.glider_time} hours, "
                f"Tow Fee: ${self.tow_fee:.2f}, Rental Fee: ${self.rental_fee:.2f}, "
                f"Remarks: {self.remarks}, Certificate: {self.certificate}, "
                f"Tow Pilot: {self.tow_pilot}, Tow Plane: {self.tow_plane}, "
                f"Flown Flag: {self.flown_flag}, Closed Flag: {self.closed_flag}")

    def __repr__(self) -> str:
        """Official string representation of the TowData instance."""
        return f"TowDataItem(ticket={self.ticket})"
