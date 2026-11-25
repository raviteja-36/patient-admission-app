import os
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import options
from .database import Base, Patient, engine, get_db
from .schemas import PatientIn, PatientOut

Base.metadata.create_all(bind=engine)  # creates the table on first start

app = FastAPI(title="Patient Admission API")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

FIELD_LABELS = {
    "name": "Name", "age": "Age", "gender": "Gender", "ward": "Ward",
    "department": "Department", "doctor": "Doctor",
    "admission_date": "Admission date", "status": "Status",
}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Turn pydantic errors into {"message": "...", "errors": {"field": "reason"}}."""
    errors = {}
    for e in exc.errors():
        loc = [p for p in e["loc"] if p != "body"]
        field = str(loc[0]) if loc else "body"
        if e["type"] == "missing":
            msg = f"{FIELD_LABELS.get(field, field)} is required"
        elif e["type"] in ("json_invalid", "model_attributes_type"):
            msg = "Request body must be valid JSON"
        else:
            msg = e["msg"].removeprefix("Value error, ")
        errors.setdefault(field, msg)
    message = "Invalid data: " + "; ".join(errors.values())
    return JSONResponse(status_code=422, content={"message": message, "errors": errors})


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail, "errors": {}})


def get_or_404(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/options")
def get_options():
    return {
        "genders": options.GENDERS, "wards": options.WARDS,
        "departments": options.DEPARTMENTS, "doctors": options.DOCTORS,
        "statuses": options.STATUSES,
    }


@app.get("/api/patients", response_model=list[PatientOut])
def list_patients(
    search: Optional[str] = None,
    ward: Optional[str] = None,
    department: Optional[str] = None,
    doctor: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Patient)
    if search and search.strip():
        q = q.filter(Patient.name.ilike(f"%{search.strip()}%"))
    if ward:
        q = q.filter(Patient.ward == ward)
    if department:
        q = q.filter(Patient.department == department)
    if doctor:
        q = q.filter(Patient.doctor == doctor)
    if status:
        q = q.filter(Patient.status == status)
    return q.order_by(Patient.admission_date.desc(), Patient.id.desc()).all()


@app.post("/api/patients", response_model=PatientOut, status_code=201)
def create_patient(data: PatientIn, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@app.get("/api/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, patient_id)


@app.put("/api/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, data: PatientIn, db: Session = Depends(get_db)):
    patient = get_or_404(db, patient_id)
    for key, value in data.model_dump().items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@app.patch("/api/patients/{patient_id}/discharge", response_model=PatientOut)
def discharge_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_or_404(db, patient_id)
    if patient.status == "Discharged":
        raise HTTPException(status_code=400, detail="Patient is already discharged")
    patient.status = "Discharged"
    db.commit()
    db.refresh(patient)
    return patient


@app.delete("/api/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = get_or_404(db, patient_id)
    db.delete(patient)
    db.commit()
    return Response(status_code=204)


# --- Serve the built React app (used in the single-service deployment) ---
STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"))

if STATIC_DIR.exists():
    if (STATIC_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = (STATIC_DIR / full_path).resolve()
        if full_path and candidate.is_file() and STATIC_DIR.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
