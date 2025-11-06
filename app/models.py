# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .database import Base
import json

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    weather_data = Column(Text, nullable=True)  # stored as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_weather(self, data: dict):
        self.weather_data = json.dumps(data)

    def get_weather(self):
        if self.weather_data:
            return json.loads(self.weather_data)
        return None
