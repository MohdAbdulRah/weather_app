# app/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict

class GeoInput(BaseModel):
    query: Optional[str] = Field(None, description="City name / ZIP code / landmark or 'lat,lon'")
    lat: Optional[float] = None
    lon: Optional[float] = None

    @validator("query", pre=True, always=True)
    def strip_query(cls, v):
        if v:
            return v.strip()
        return v

class WeatherRequest(BaseModel):
    location: GeoInput
    start_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    save: Optional[bool] = Field(False, description="Whether to store this request into DB")

class RecordCreate(BaseModel):
    location_name: str
    lat: float
    lon: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class RecordOut(BaseModel):
    id: int
    location_name: str
    lat: float
    lon: float
    start_date: Optional[str]
    end_date: Optional[str]
    weather_data: Optional[Dict[str, Any]]
    created_at: str

    class Config:
        orm_mode = True
