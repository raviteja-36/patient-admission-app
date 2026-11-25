"""Optional: python -m app.seed  -> adds a few sample patients if the table is empty."""
from datetime import date, timedelta

from .database import Base, Patient, SessionLocal, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if db.query(Patient).count() == 0:
    today = date.today()
    rows = [
        ("Ravi Kumar", 54, "Male", "ICU", "Cardiology", "Dr. Anita Sharma", 2, "Admitted"),
        ("Meera Reddy", 31, "Female", "Maternity", "Gynecology", "Dr. Priya Nair", 1, "Admitted"),
        ("Aarav Gupta", 7, "Male", "Pediatric Ward", "Pediatrics", "Dr. Sneha Iyer", 4, "Admitted"),
        ("Sunita Devi", 68, "Female", "General Ward", "General Medicine", "Dr. Rohan Mehta", 9, "Discharged"),
        ("Imran Khan", 42, "Male", "Surgical Ward", "Orthopedics", "Dr. Arjun Singh", 3, "Admitted"),
        ("Lakshmi Narayan", 59, "Female", "Emergency", "Neurology", "Dr. Vikram Rao", 0, "Admitted"),
    ]
    for n, a, g, w, d, doc, ago, s in rows:
        db.add(Patient(name=n, age=a, gender=g, ward=w, department=d, doctor=doc,
                       admission_date=today - timedelta(days=ago), status=s))
    db.commit()
    print("Seeded sample patients")
db.close()
