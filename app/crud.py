# app/crud.py
from sqlalchemy.orm import Session
from . import models
from typing import Optional, Dict

def create_record(db: Session, location_name: str, lat: float, lon: float, start_date: Optional[str], end_date: Optional[str], weather_data: Optional[dict]):
    rec = models.Record(
        location_name=location_name,
        lat=lat,
        lon=lon,
        start_date=start_date,
        end_date=end_date
    )
    if weather_data is not None:
        rec.set_weather(weather_data)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_record(db: Session, record_id: int):
    return db.query(models.Record).filter(models.Record.id == record_id).first()

def list_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Record).offset(skip).limit(limit).all()

def update_record(db: Session, record_id: int, fields: dict):
    rec = get_record(db, record_id)
    if not rec:
        return None
    for k, v in fields.items():
        if k == "weather_data":
            rec.set_weather(v)
        elif hasattr(rec, k):
            setattr(rec, k, v)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def delete_record(db: Session, record_id: int):
    rec = get_record(db, record_id)
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True
