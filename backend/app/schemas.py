import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_validator

from .options import DEPARTMENTS, DOCTORS, GENDERS, STATUSES, WARDS

NAME_RE = re.compile(r"^[A-Za-z]+(?: [A-Za-z]+)*$")  # letters, single spaces between words


def today_ist() -> date:
    return datetime.now(ZoneInfo("Asia/Kolkata")).date()


def _select(label: str, allowed: list[str]):
    def check(v):
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"{label} is required")
        if v not in allowed:
            raise ValueError(f"{label} must be one of: {', '.join(allowed)}")
        return v
    return check


class PatientIn(BaseModel):
    name: str
    age: int
    gender: str
    ward: str
    department: str
    doctor: str
    admission_date: date
    status: str = "Admitted"

    @field_validator("name", mode="before")
    @classmethod
    def v_name(cls, v):
        if v is None or not isinstance(v, str) or not v.strip():
            raise ValueError("Name is required")
        v = " ".join(v.split())  # trim + collapse extra spaces
        if not NAME_RE.match(v):
            raise ValueError("Name can contain letters and spaces only")
        if len(v) > 100:
            raise ValueError("Name must be 100 characters or fewer")
        return v

    @field_validator("age", mode="before")
    @classmethod
    def v_age(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("Age is required")
        if isinstance(v, bool):
            raise ValueError("Age must be a number")
        try:
            n = float(v)
        except (TypeError, ValueError):
            raise ValueError("Age must be a number")
        if not n.is_integer():
            raise ValueError("Age must be a whole number")
        n = int(n)
        if n < 0 or n > 120:
            raise ValueError("Age must be between 0 and 120")
        return n

    @field_validator("gender", mode="before")
    @classmethod
    def v_gender(cls, v):
        return _select("Gender", GENDERS)(v)

    @field_validator("ward", mode="before")
    @classmethod
    def v_ward(cls, v):
        return _select("Ward", WARDS)(v)

    @field_validator("department", mode="before")
    @classmethod
    def v_department(cls, v):
        return _select("Department", DEPARTMENTS)(v)

    @field_validator("doctor", mode="before")
    @classmethod
    def v_doctor(cls, v):
        return _select("Doctor", DOCTORS)(v)

    @field_validator("status", mode="before")
    @classmethod
    def v_status(cls, v):
        return _select("Status", STATUSES)(v)

    @field_validator("admission_date", mode="before")
    @classmethod
    def v_date(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("Admission date is required")
        if isinstance(v, str):
            try:
                v = date.fromisoformat(v)
            except ValueError:
                raise ValueError("Admission date must be a valid date (YYYY-MM-DD)")
        if not isinstance(v, date):
            raise ValueError("Admission date must be a valid date (YYYY-MM-DD)")
        if v > today_ist():
            raise ValueError("Admission date cannot be in the future")
        return v


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: str
    ward: str
    department: str
    doctor: str
    admission_date: date
    status: str
