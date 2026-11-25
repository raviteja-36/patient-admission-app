"""Dropdown values. The frontend loads these from /api/options and the backend
validates against the same lists, so both sides always agree."""

GENDERS = ["Male", "Female", "Other"]

WARDS = ["General Ward", "ICU", "Emergency", "Maternity", "Pediatric Ward", "Surgical Ward"]

DEPARTMENTS = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics",
    "General Medicine", "Gynecology", "Oncology",
]

DOCTORS = [
    "Dr. Anita Sharma", "Dr. Rohan Mehta", "Dr. Priya Nair",
    "Dr. Vikram Rao", "Dr. Sneha Iyer", "Dr. Arjun Singh",
]

STATUSES = ["Admitted", "Discharged"]
