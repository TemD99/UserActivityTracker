from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATABASE_PATH = ""
if os.name == 'nt':
   DATABASE_PATH = r"C:\Users\Analy\datamules\UserActivityTracker\data\user_activity.db"
elif os.name == 'posix':
   DATABASE_PATH = "/home/wiz/datamules/UserActivityTracker/data/user_activity.db"
else:
    print("Unknown operating system.")
# Database Path

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Ensure database exists
if not os.path.exists(DATABASE_PATH):
    raise FileNotFoundError(f"Database not found at {DATABASE_PATH}")

# Setup SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Define the UserActivity table model
class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    WindowTitle = Column(String)
    StartTime = Column(String)
    EndTime = Column(String)
    DurationSec = Column(Float)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to format hour into 12-hour format with AM/PM
def format_hour(hour):
    hour = int(hour)
    if hour == 0:
        return "12 AM - 1 AM"
    elif hour < 12:
        return f"{hour} AM - {hour + 1} AM"
    elif hour == 12:
        return "12 PM - 1 PM"
    else:
        return f"{hour - 12} PM - {hour - 11} PM"

# API Route to get aggregated user activity along with total tasks, most active hour, peak hour, and long session tracking
@app.get("/api/get_activity")
def get_activity(
    db: Session = Depends(get_db),
    specific_date: str = Query(None, description="Date in YYYY-MM-DD format"),
    limit: int = Query(10, description="Number of results to return"),
):
    try:
        if specific_date:
            start_time = f"{specific_date} 00:00:00"
            end_time = f"{specific_date} 23:59:59"

            # Fetch activity data for the specific date
            results = (
                db.query(UserActivity.WindowTitle, func.sum(UserActivity.DurationSec).label("total_time"))
                .filter(UserActivity.StartTime >= start_time, UserActivity.StartTime <= end_time)
                .group_by(UserActivity.WindowTitle)
                .order_by(func.sum(UserActivity.DurationSec).desc())
                .limit(limit)
                .all()
            )

            # Count the number of unique activities
            unique_activities = (
                db.query(func.count(func.distinct(UserActivity.WindowTitle)))
                .filter(UserActivity.StartTime >= start_time, UserActivity.StartTime <= end_time)
                .scalar()
            )

            # Get the most active hour of the day and format it
            active_time_data = (
                db.query(func.strftime("%H", UserActivity.StartTime).label("active_hour"),
                        func.sum(UserActivity.DurationSec).label("total_time"))
                .filter(UserActivity.StartTime >= start_time, UserActivity.StartTime <= end_time)
                .group_by("active_hour")
                .order_by(func.sum(UserActivity.DurationSec).desc())
                .first()
            )
            most_active_hour = format_hour(active_time_data[0]) if active_time_data else "No Data"

            # Get the peak hour and the most used activity during that hour
            peak_activity_data = (
                db.query(func.strftime("%H", UserActivity.StartTime).label("peak_hour"),
                        UserActivity.WindowTitle,
                        func.sum(UserActivity.DurationSec).label("total_time"))
                .filter(UserActivity.StartTime >= start_time, UserActivity.StartTime <= end_time)
                .group_by("peak_hour", UserActivity.WindowTitle)
                .order_by(func.sum(UserActivity.DurationSec).desc())
                .first()
            )
            peak_hour = format_hour(peak_activity_data[0]) if peak_activity_data else "No Data"
            peak_activity = peak_activity_data[1] if peak_activity_data else "No Data"

            # Get activities that lasted more than an hour (3600 seconds)
            long_sessions = (
                db.query(UserActivity.WindowTitle, func.sum(UserActivity.DurationSec).label("total_time"))
                .filter(UserActivity.StartTime >= start_time, UserActivity.StartTime <= end_time)
                .group_by(UserActivity.WindowTitle)
                .having(func.sum(UserActivity.DurationSec) > 3600)
                .order_by(func.sum(UserActivity.DurationSec).desc())
                .all()
            )

            return {
                "activity": [{"window_title": row[0], "total_time": row[1]} for row in results],
                "total_tasks": unique_activities,
                "most_active_hour": most_active_hour,
                "peak_hour": peak_hour,
                "peak_activity": peak_activity,
                "long_sessions": [{"window_title": row[0], "total_time": row[1]} for row in long_sessions]
            }

        raise HTTPException(status_code=400, detail="specific_date parameter is required.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root route for health check
@app.get("/")
def home():
    return {"message": "User Activity API is running!"}
