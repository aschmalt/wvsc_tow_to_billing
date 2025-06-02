from dataclasses import dataclass, field


@dataclass
class TowData:
    """
    Class to hold TOW data from Tow Ticket System.
    """
    tow: float = field(default=0.0, metadata={
                       "description": "Time of Week in seconds"})
    week: int = field(default=0, metadata={"description": "GPS week number"})
    leap_seconds: int = field(
        default=0, metadata={"description": "Number of leap seconds"})

    def __post_init__(self):
        if self.tow < 0:
            raise ValueError("TOW must be a non-negative value.")
        if self.week < 0:
            raise ValueError("Week number must be a non-negative integer.")
        if self.leap_seconds < 0:
            raise ValueError("Leap seconds must be a non-negative integer.")
