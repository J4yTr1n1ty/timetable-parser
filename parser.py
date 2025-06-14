import pdfplumber
import re
from typing import List, Dict, Optional

from models import TimetableEntry


class TimetableParser:
    """
    Parses extracted timetable data from PDF tables into structured course entries.
    """

    def __init__(self):
        self.date_pattern = r"(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag), \d{1,2}\. \w+ \d{4}"
        self.time_pattern = r"\d{2}:\d{2}-\d{2}:\d{2}"
        self.course_pattern = r"([A-Z\s]+)\s*/\s*([A-Z0-9]+)"
        self.remote_keywords = ["remote", "teams", "coaching.*remote"]

    def is_remote_class(self, entry: str) -> bool:
        """
        Determines if a class entry represents a remote/online class.

        Args:
            entry: The class entry string to check

        Returns:
            True if the class is remote, False otherwise
        """
        if not entry:
            return False
        entry_lower = entry.lower()
        return any(keyword in entry_lower for keyword in self.remote_keywords)

    def extract_course_info(self, entry: str) -> Optional[tuple]:
        """
        Extracts course code and room from a timetable entry.

        Args:
            entry: Raw timetable entry string

        Returns:
            Tuple of (course_code, room) or None if no match found
        """
        if not entry or entry.strip() == "":
            return None

        if self.is_remote_class(entry):
            match = re.search(r"([A-Z\s]+)", entry)
            if match:
                course_code = match.group(1).strip()
                return (course_code, "Teams")

        match = re.search(self.course_pattern, entry)
        if match:
            course_code = match.group(1).strip()
            room = match.group(2).strip()
            return (course_code, room)

        return None

    def parse_raw_data(self, raw_data: List[List]) -> List[TimetableEntry]:
        """
        Parses raw table data extracted from PDF into structured timetable entries.

        Args:
            raw_data: List of rows, where each row is a list of cell values

        Returns:
            List of TimetableEntry objects
        """
        entries = []
        current_date = None
        current_week = None
        class_groups = []

        for row in raw_data:
            if not row:
                continue

            row_str = " ".join(str(cell) if cell else "" for cell in row)

            # Extract week number
            if "WOCHEN" in row_str:
                continue
            if row_str.strip().isdigit():
                current_week = int(row_str.strip())
                continue

            # Extract class group headers
            if any(
                group in row_str for group in ["25A", "25B", "25C", "24A", "24B", "24C"]
            ):
                class_groups = [cell for cell in row if cell and cell.strip()]
                continue

            # Extract date
            date_match = re.search(self.date_pattern, row_str)
            if date_match:
                current_date = date_match.group()
                continue

            # Extract time and course entries
            time_match = re.search(self.time_pattern, row_str)
            if time_match and current_date:
                time_slot = time_match.group()

                # Process each cell in the row for course information
                for i, cell in enumerate(
                    row[2:], start=2
                ):  # Skip first two columns (date/time)
                    if cell and cell.strip():
                        course_info = self.extract_course_info(str(cell))
                        if course_info:
                            course_code, room = course_info

                            # Determine class group based on column position
                            group_index = i - 2
                            class_group = (
                                class_groups[group_index]
                                if group_index < len(class_groups)
                                else "Unknown"
                            )

                            entries.append(
                                TimetableEntry(
                                    date=current_date,
                                    time=time_slot,
                                    course_code=course_code,
                                    room=room,
                                    class_group=class_group,
                                    week=current_week,
                                )
                            )

        return entries

    def parse_pdf(self, pdf_path: str) -> List[TimetableEntry]:
        """
        Extracts and parses timetable data from a PDF file.

        Args:
            pdf_path: Path to the PDF file containing the timetable

        Returns:
            List of TimetableEntry objects
        """
        raw_data = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    raw_data.extend(table)

        return self.parse_raw_data(raw_data)

    def to_calendar_format(self, entries: List[TimetableEntry]) -> List[Dict]:
        """
        Converts TimetableEntry objects to calendar event format.

        Args:
            entries: List of TimetableEntry objects

        Returns:
            List of dictionaries formatted for calendar events
        """
        calendar_events = []

        for entry in entries:
            # Parse date for proper formatting
            try:
                # Handle German date format
                date_parts = entry.date.split(", ")[1]  # Remove day name
                formatted_date = entry.date  # For now, keep original format
            except (ValueError, IndexError):
                formatted_date = entry.date

            # Parse time slots
            start_time, end_time = entry.time.split("-")

            event = {
                "title": entry.course_code,
                "date": formatted_date,
                "start_time": start_time,
                "end_time": end_time,
                "location": "Microsoft Teams"
                if entry.room == "Teams"
                else f"Room {entry.room}",
                "description": f"Class: {entry.class_group}",
                "is_online": entry.room == "Teams",
                "week": entry.week,
            }

            calendar_events.append(event)

        return calendar_events

    def to_dict_list(self, entries: List[TimetableEntry]) -> List[Dict]:
        """
        Converts TimetableEntry objects to a list of dictionaries for easy serialization.

        Args:
            entries: List of TimetableEntry objects

        Returns:
            List of dictionaries representing the timetable entries
        """
        return [
            {
                "date": entry.date,
                "time": entry.time,
                "course_code": entry.course_code,
                "room": entry.room,
                "class_group": entry.class_group,
                "week": entry.week,
            }
            for entry in entries
        ]
