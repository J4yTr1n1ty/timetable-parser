from icalendar import Calendar, Event, vText
from datetime import datetime, date, time as dt_time
import pytz
from typing import List, Tuple
import re

from models import TimetableEntry


class ICSExporter:
    """
    Exports timetable entries to ICS (iCalendar) format.
    """

    def __init__(self, timezone: str = "Europe/Vienna"):
        self.timezone = pytz.timezone(timezone)
        self.german_months = {
            "Januar": 1,
            "Februar": 2,
            "März": 3,
            "April": 4,
            "Mai": 5,
            "Juni": 6,
            "Juli": 7,
            "August": 8,
            "September": 9,
            "Oktober": 10,
            "November": 11,
            "Dezember": 12,
        }

    def parse_german_date(self, date_str: str) -> date:
        """
        Parses German date format like "Donnerstag, 14. August 2025".

        Args:
            date_str: German formatted date string

        Returns:
            date object
        """
        try:
            # Remove day name and extract date part
            date_part = date_str.split(", ")[1]

            # Parse "14. August 2025"
            match = re.match(r"(\d{1,2})\.\s+(\w+)\s+(\d{4})", date_part)
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))

                month = self.german_months.get(month_name)
                if month:
                    return date(year, month, day)

            raise ValueError(f"Could not parse date: {date_str}")

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid date format: {date_str}") from e

    def parse_time(self, time_str: str) -> Tuple[dt_time, dt_time]:
        """
        Parses time range like "17:30-19:00".

        Args:
            time_str: Time range string

        Returns:
            Tuple of (start_time, end_time)
        """
        try:
            start_str, end_str = time_str.split("-")

            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))

            return dt_time(start_hour, start_min), dt_time(end_hour, end_min)

        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}") from e

    def create_event(self, entry: TimetableEntry) -> Event:
        """
        Creates an ICS event from a timetable entry.

        Args:
            entry: TimetableEntry object

        Returns:
            icalendar Event object
        """
        event = Event()

        # Parse date and time
        event_date = self.parse_german_date(entry.date)
        start_time, end_time = self.parse_time(entry.time)

        # Create datetime objects with timezone
        start_dt = self.timezone.localize(datetime.combine(event_date, start_time))
        end_dt = self.timezone.localize(datetime.combine(event_date, end_time))

        # Set event properties
        event.add("summary", f"{entry.course_code} ({entry.class_group})")
        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)

        # Set location
        if entry.room == "Teams":
            event.add("location", "Microsoft Teams (Online)")
            event.add("description", f"Online class for {entry.class_group}")
        else:
            event.add("location", f"Room {entry.room}")
            event.add("description", f"Class: {entry.class_group}\nRoom: {entry.room}")

        # Add additional metadata
        if entry.week:
            current_desc = str(event.get("description", ""))
            event["description"] = f"{current_desc}\nWeek: {entry.week}"

        # Generate unique ID
        event.add(
            "uid", f"{entry.course_code}-{entry.class_group}-{event_date}-{start_time}"
        )

        return event

    def export_to_ics(self, entries: List[TimetableEntry], filename: str = None) -> str:
        """
        Exports timetable entries to ICS format.

        Args:
            entries: List of TimetableEntry objects
            filename: Optional filename to save the ICS file

        Returns:
            ICS content as string
        """
        # Create calendar
        cal = Calendar()
        cal.add("prodid", "-//Timetable Parser//University Schedule//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")
        cal.add("x-wr-calname", "University Timetable")
        cal.add("x-wr-timezone", str(self.timezone))

        # Add events
        for entry in entries:
            try:
                event = self.create_event(entry)
                cal.add_component(event)
            except ValueError as e:
                print(f"Skipping invalid entry: {e}")
                continue

        # Generate ICS content
        ics_content = cal.to_ical().decode("utf-8")

        # Save to file if filename provided
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(ics_content)
            print(f"Calendar exported to {filename}")

        return ics_content

    def export_by_class_group(
        self, entries: List[TimetableEntry], class_group: str, filename: str = None
    ) -> str:
        """
        Exports timetable entries for a specific class group to ICS format.

        Args:
            entries: List of TimetableEntry objects
            class_group: Class group to filter by (e.g., "25A")
            filename: Optional filename to save the ICS file

        Returns:
            ICS content as string
        """
        filtered_entries = [e for e in entries if e.class_group == class_group]

        if not filtered_entries:
            print(f"No entries found for class group {class_group}")
            return ""

        if not filename:
            filename = f"timetable_{class_group.lower()}.ics"

        print(f"Exporting {len(filtered_entries)} events for class {class_group}")
        return self.export_to_ics(filtered_entries, filename)
