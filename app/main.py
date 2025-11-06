# app/main.py
import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import io, csv, json
from dicttoxml import dicttoxml
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dateutil.parser import parse as parse_date

load_dotenv()

from . import models, crud, services
from .database import engine, get_db
from .schemas import WeatherRequest, RecordCreate, RecordOut

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather App - Tech Assessment")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/weather/search")
def weather_search(payload: WeatherRequest, db: Session = Depends(get_db)):
    try:
        loc = payload.location.dict()
        lat, lon, name = services.parse_location_input(loc)

        current = services.fetch_current_weather(lat, lon)
        forecast = services.fetch_5day_forecast(lat, lon)

        historical = None
        if payload.start_date and payload.end_date:
            # validate date format and order
            try:
                sd = parse_date(payload.start_date).date()
                ed = parse_date(payload.end_date).date()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
            if sd > ed:
                raise HTTPException(status_code=400, detail="start_date must be <= end_date")
            historical = services.fetch_historical_temperatures(lat, lon, payload.start_date, payload.end_date)

        result = {
            "location_name": name,
            "lat": lat, "lon": lon,
            "current": current,
            "forecast": forecast,
            "historical": historical,
            "youtube_search": services.youtube_search_url_for_location(name),
            "google_maps_embed": services.google_maps_embed_url(lat, lon)
        }

        rec = None
        if payload.save:
            rec = crud.create_record(db, name, lat, lon, payload.start_date, payload.end_date, result)

        response = {"result": result}
        if rec:
            response["saved_record_id"] = rec.id
        return response
    except services.OpenWeatherError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/records", response_model=RecordOut)
def create_record(rc: RecordCreate, db: Session = Depends(get_db)):
    try:
        current = services.fetch_current_weather(rc.lat, rc.lon)
        forecast = services.fetch_5day_forecast(rc.lat, rc.lon)
        historical = None
        if rc.start_date and rc.end_date:
            # validate
            try:
                sd = parse_date(rc.start_date).date()
                ed = parse_date(rc.end_date).date()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid date format.")
            if sd > ed:
                raise HTTPException(status_code=400, detail="start_date <= end_date required")
            historical = services.fetch_historical_temperatures(rc.lat, rc.lon, rc.start_date, rc.end_date)

        combined = {
            "current": current,
            "forecast": forecast,
            "historical": historical,
            "youtube_search": services.youtube_search_url_for_location(rc.location_name),
            "google_maps_embed": services.google_maps_embed_url(rc.lat, rc.lon)
        }
        rec = crud.create_record(db, rc.location_name, rc.lat, rc.lon, rc.start_date, rc.end_date, combined)
        return RecordOut(
            id=rec.id,
            location_name=rec.location_name,
            lat=rec.lat,
            lon=rec.lon,
            start_date=rec.start_date,
            end_date=rec.end_date,
            weather_data=rec.get_weather(),
            created_at=str(rec.created_at)
        )
    except services.OpenWeatherError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/records")
def list_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recs = crud.list_records(db, skip=skip, limit=limit)
    out = []
    for r in recs:
        out.append({
            "id": r.id,
            "location_name": r.location_name,
            "lat": r.lat,
            "lon": r.lon,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "weather_data": r.get_weather(),
            "created_at": str(r.created_at)
        })
    return {"records": out}

@app.get("/api/records/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):
    rec = crud.get_record(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": rec.id,
        "location_name": rec.location_name,
        "lat": rec.lat,
        "lon": rec.lon,
        "start_date": rec.start_date,
        "end_date": rec.end_date,
        "weather_data": rec.get_weather(),
        "created_at": str(rec.created_at)
    }

@app.put("/api/records/{record_id}")
def update_record(record_id: int, payload: dict, db: Session = Depends(get_db)):
    allowed = {"location_name", "lat", "lon", "start_date", "end_date", "weather_data"}
    patch = {k: v for k, v in payload.items() if k in allowed}
    if not patch:
        raise HTTPException(status_code=400, detail="No valid fields to update.")
    rec = crud.update_record(db, record_id, patch)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "updated", "record_id": rec.id}

@app.delete("/api/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_record(db, record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "deleted"}

@app.get("/api/records/{record_id}/export")
def export_record(record_id: int, format: str = "json", db: Session = Depends(get_db)):
    rec = crud.get_record(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    data = {
        "id": rec.id,
        "location_name": rec.location_name,
        "lat": rec.lat,
        "lon": rec.lon,
        "start_date": rec.start_date,
        "end_date": rec.end_date,
        "weather_data": rec.get_weather(),
        "created_at": str(rec.created_at)
    }
    fmt = format.lower()
    if fmt == "json":
        return JSONResponse(content=data)
    elif fmt == "csv":
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(["id","location_name","lat","lon","start_date","end_date","created_at","weather_json"])
        writer.writerow([data["id"], data["location_name"], data["lat"], data["lon"], data["start_date"], data["end_date"], data["created_at"], json.dumps(data["weather_data"])])
        output = si.getvalue().encode("utf-8")
        return StreamingResponse(io.BytesIO(output), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=record_{rec.id}.csv"})
    elif fmt == "xml":
        xml_bytes = dicttoxml(data, custom_root='record', attr_type=False)
        return StreamingResponse(io.BytesIO(xml_bytes), media_type="application/xml", headers={"Content-Disposition": f"attachment; filename=record_{rec.id}.xml"})
    elif fmt == "pdf":
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        x = 40
        y = 750
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, f"Weather Record #{data['id']} - {data['location_name']}")
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(x, y, f"Latitude: {data['lat']}   Longitude: {data['lon']}")
        y -= 20
        c.drawString(x, y, f"Date Range: {data['start_date']} to {data['end_date']}")
        y -= 20
        c.drawString(x, y, f"Created at: {data['created_at']}")
        y -= 30
        wd = json.dumps(data['weather_data'], indent=2)
        for line in wd.splitlines():
            if y < 60:
                c.showPage()
                y = 750
            # truncate long lines a bit
            c.drawString(x, y, line[:120])
            y -= 12
        c.save()
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=record_{rec.id}.pdf"})
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Choose json, csv, xml, or pdf.")

@app.get("/api/health")
def health():
    return {"status": "ok"}
