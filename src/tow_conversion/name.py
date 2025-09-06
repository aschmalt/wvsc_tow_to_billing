"""A module to handle names in multiple formats."""
from dataclasses import dataclass


@dataclass
class Name:
    """Class to hold a name and be able to get it in Last, First format."""

    name: str

    def __post_init__(self) -> None:
        """Post-initialization validation for the Name class."""
        self.last = ''
        self.first = ''

        if ',' in self.name:
            parts = self.name.split(',')
            if len(parts) != 2:
                raise ValueError("Name must be in 'Last, First' format.")
            self.last = parts[0].strip()
            self.first = parts[1].strip()
        elif ' ' in self.name:
            parts = self.name.split()
            self.first = ' '.join(parts[:-1]).strip()
            self.last = parts[-1].strip()

    def __str__(self) -> str:
        """
        Return the name in Last, First format if both parts are available.

        If not, return the original name.
        """
        if self.first and self.last:
            return f"{self.last}, {self.first}"
        return self.name

    def __eq__(self, value: object) -> bool:
        """Check if two Name objects are equal based on last and first names."""
        if isinstance(value, str):
            value = Name(value)

        if not isinstance(value, Name):
            return NotImplemented

        if not self.last and not self.first and not value.last and not value.first:
            # Both first and last names are empty
            return self.name == value.name
        return (self.last, self.first) == (value.last, value.first)

    def __hash__(self) -> int:
        """Return a hash of the name."""
        return hash((self.last, self.first))

    def __lt__(self, other: object) -> bool:
        """Compare two Name objects based on last and first names."""
        if isinstance(other, str):
            other = Name(other)

        if not isinstance(other, Name):
            return NotImplemented

        if not self.last and not self.first and not other.last and not other.first:
            # Both first and last names are empty
            return self.name < other.name
        if not self.last and not self.first:
            # If self has no name, compare with other last name
            return self.name < other.last
        if not other.last and not other.first:
            # If other has no name, compare with self last name
            return self.last < other.name
        return (self.last, self.first) < (other.last, other.first)
