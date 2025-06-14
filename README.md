# Timetable Parser

A simple Python tool to parse university timetables from PDF files and extract course schedules for specific class groups.

## Features

- Extracts course codes, room numbers, and time slots from PDF timetables
- Automatically detects remote/Teams classes
- Filters schedules by class group (25A, 25B, 24A, etc.)
- Outputs calendar-ready event format
- **Exports to ICS (iCalendar) format** for importing into calendar apps

## Project Structure

```
├── main.py             # Entry point
├── models.py           # Data models
├── parser.py           # Core parsing logic
├── ics_exporter.py     # ICS/iCalendar export functionality
├── export_example.py   # Example usage for ICS export
├── __init__.py         # Package initialization
├── pyproject.toml      # Dependencies
└── .gitignore          # Git ignore patterns
```

## Installation

```bash
uv sync
```

## Usage

Place your timetable PDF as `StundenplanHS2025-26.pdf` in the project root and run:

```bash
uv run python main.py
```

Or modify the `class_group` variable in `main.py` to filter for your specific class.

### Export to Calendar

The script automatically creates an ICS file that you can import into:

- Google Calendar
- Outlook
- Apple Calendar
- Any calendar app supporting iCalendar format

The generated file will be named `timetable_25a.ics` (based on your class group).

## Example Output

```
📅 Donnerstag, 14. August 2025
⏰ 17:30-19:00
📚 OOP
📍 Room IE306
---
```

## License

AGPL-3.0
