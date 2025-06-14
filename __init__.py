"""
Timetable Parser

A simple Python tool to parse university timetables from PDF files.
"""

from .models import TimetableEntry
from .parser import TimetableParser
from .ics_exporter import ICSExporter

__version__ = "0.1.0"
__all__ = ["TimetableEntry", "TimetableParser", "ICSExporter"]
