from dataclasses import dataclass
from typing import Optional


@dataclass
class TimetableEntry:
    """
    Represents a single timetable entry with course information.

    Attributes:
        date: The date of the class
        time: Time slot (e.g., "17:30-19:00")
        course_code: Course identifier (e.g., "OOP")
        room: Room location or "Teams" for remote classes
        class_group: Class group identifier (e.g., "25A", "24B")
        week: Week number if available
    """

    date: str
    time: str
    course_code: str
    room: str
    class_group: str
    week: Optional[int] = None
