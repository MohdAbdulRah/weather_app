# Weather App - AI Engineer Intern Technical Assessment

## ✅ Overview

This project is a Weather Application built as part of the **AI Engineer Intern Technical Assessment**.  
It fulfills requirements for **Tech Assessment 1** and includes parts of **Tech Assessment 2**.

---

## ✅ Features Implemented

### 🌦 Weather Functionality
- Users can enter a location using:
  - City/Town Name
  - Zip/Postal Code
  - Coordinates (Latitude, Longitude)
  - Landmark or custom query
- Fetches **real-time current weather** data.
- Added **5-day forecast**.
- Supports **weather icons and UI display**.
- Detects **user's current location (geolocation-based)**.

---

### 💾 CRUD (Tech Assessment 2 – Core Requirement)
Uses **SQLite + SQLAlchemy** for database persistence.

| Operation | Description |
|-----------|-------------|
| ✅ CREATE | Save weather request with location + date range |
| ✅ READ   | List all past stored weather records |
| ✅ UPDATE | Modify saved records (location, dates, weather info) |
| ✅ DELETE | Remove any saved record |

---

### 🌍 Additional Enhancements  
- Export saved data as **JSON or CSV**.  
- Added **Info Popup + Developer Name** inside UI.  
- Info section shows description of **PM Accelerator**.  

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend   | FastAPI |
| Database  | SQLite + SQLAlchemy |
| API       | OpenWeatherMap API |
| Frontend  | HTML + Jinja2 Templates + JS |
| Environment | Python, dotenv |

---

## 📁 Project Structure

```
app/
 ├── main.py           # FastAPI routes
 ├── models.py         # Database schema
 ├── schemas.py        # Pydantic models
 ├── services.py       # API logic & validation
 ├── crud.py           # Database operations
 ├── database.py       # DB connection & session
 ├── templates/        # Frontend HTML files
 └── static/           # CSS, JS, images
```

---

## 🚀 How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone <repo-link>
cd weather-app
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Add API Key
Create a `.env` file:
```
OPENWEATHER_API_KEY=your_api_key_here
```

### 5️⃣ Start the FastAPI server
```bash
uvicorn app.main:app --reload
```

### 6️⃣ Open in Browser
```
http://127.0.0.1:8000
```

---

## 📝 API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/weather/search` | Fetch weather + (optional save) |
| GET    | `/api/records` | List all saved records |
| POST   | `/api/records` | Create new weather record |
| GET    | `/api/records/{id}` | Retrieve a record |
| PUT    | `/api/records/{id}` | Update a record |
| DELETE | `/api/records/{id}` | Delete a record |
| GET    | `/api/records/{id}/export` | Export record (JSON/CSV) |
| GET    | `/api/health` | Health check |

---

## 📌 PM Accelerator Info (as shown in app)

> **PM Accelerator (Product Manager Accelerator)** is a platform helping aspiring product managers gain real-world product development experience, mentorship, and industry guidance. It bridges the gap between learning and real product-building using AI and innovation strategies.

---

## 👤 Developer

**Developed by:** Mohd Abdul Rahman 
Feel free to connect on LinkedIn or GitHub!

---

## ✅ Assessment Status

| Assessment | Status |
|------------|--------|
| Tech Assessment 1 | ✅ Completed |
| Tech Assessment 2 (CRUD, Export) | ✅ Completed |
| Additional APIs/Enhancements | ✅ Started |

---

## 📩 Contact / Future Improvements
- Add Google Maps integration
- Add YouTube travel recommendations API
- Enable PDF/Markdown export
- Deploy using Docker or Render

---
