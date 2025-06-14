from parser import TimetableParser
from ics_exporter import ICSExporter


def main():
    parser = TimetableParser()

    try:
        entries = parser.parse_pdf("StundenplanHS2025-26.pdf")
        print(f"Found {len(entries)} timetable entries:")
    except FileNotFoundError:
        print("PDF file not found. Using sample data...")

    if entries:
        class_group = "25A"  # Change this to your target class
        filtered_entries = [e for e in entries if e.class_group == class_group]

        print(f"\nEntries for class {class_group}:")
        print(f"Found {len(filtered_entries)} entries")
        for entry in filtered_entries:
            location = "Teams" if entry.room == "Teams" else f"Room {entry.room}"
            print(f"📅 {entry.date}")
            print(f"⏰ {entry.time}")
            print(f"📚 {entry.course_code}")
            print(f"📍 {location}")
            print("---")

        if filtered_entries:
            print(f"\nExporting {class_group} schedule to ICS...")
            exporter = ICSExporter()
            exporter.export_by_class_group(entries, class_group)


if __name__ == "__main__":
    main()
