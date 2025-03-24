from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from contextlib import asynccontextmanager

# --- Database setup ---

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database models ---

class DriverDB(Base):
    __tablename__ = "drivers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    laps = relationship("LapDB", back_populates="driver", cascade="all, delete-orphan")

class LapDB(Base):
    __tablename__ = "laps"
    id = Column(String, primary_key=True, index=True)
    lap_time = Column(Float, nullable=False)
    track = Column(String, nullable=False)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=False)
    driver = relationship("DriverDB", back_populates="laps")

Base.metadata.create_all(bind=engine)

# --- Pydantic schemas ---

# Driver schemas
class DriverBase(BaseModel):
    name: str

class DriverCreate(DriverBase):
    pass

class DriverUpdate(DriverBase):
    pass

class Lap(BaseModel):
    id: Optional[str]
    lap_time: float
    track: str

    class Config:
        from_attributes = True

class Driver(DriverBase):
    id: Optional[str]
    laps: List[Lap] = []

    class Config:
        from_attributes = True

# Lap schemas
class LapCreate(BaseModel):
    lap_time: float
    track: str

class LapUpdate(BaseModel):
    lap_time: float
    track: str

# --- Dependency for DB session ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FastAPI application setup with lifespan handler ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Add dummy data if none exists
    db = SessionLocal()
    try:
        if db.query(DriverDB).count() == 0:
            driver = DriverDB(id=str(uuid.uuid4()), name="Lewis Hamilton")
            lap1 = LapDB(id=str(uuid.uuid4()), lap_time=85.4, track="Silverstone", driver=driver)
            lap2 = LapDB(id=str(uuid.uuid4()), lap_time=86.2, track="Monza", driver=driver)
            driver.laps = [lap1, lap2]
            db.add(driver)
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

# ---------- Driver Endpoints ----------

@app.post("/drivers", response_model=Driver)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = DriverDB(id=str(uuid.uuid4()), name=driver.name)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@app.get("/drivers", response_model=List[Driver])
def get_drivers(db: Session = Depends(get_db)):
    return db.query(DriverDB).all()

@app.get("/drivers/{driver_id}", response_model=Driver)
def get_driver(driver_id: str, db: Session = Depends(get_db)):
    driver = db.query(DriverDB).filter(DriverDB.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@app.put("/drivers/{driver_id}", response_model=Driver)
def update_driver(driver_id: str, driver_update: DriverUpdate, db: Session = Depends(get_db)):
    driver = db.query(DriverDB).filter(DriverDB.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.name = driver_update.name
    db.commit()
    db.refresh(driver)
    return driver

@app.delete("/drivers/{driver_id}")
def delete_driver(driver_id: str, db: Session = Depends(get_db)):
    driver = db.query(DriverDB).filter(DriverDB.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return {"detail": "Driver deleted"}

# ---------- Lap Endpoints ----------

@app.post("/drivers/{driver_id}/laps", response_model=Lap)
def create_lap(driver_id: str, lap: LapCreate, db: Session = Depends(get_db)):
    driver = db.query(DriverDB).filter(DriverDB.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db_lap = LapDB(id=str(uuid.uuid4()), lap_time=lap.lap_time, track=lap.track, driver_id=driver_id)
    db.add(db_lap)
    db.commit()
    db.refresh(db_lap)
    return db_lap

@app.get("/drivers/{driver_id}/laps", response_model=List[Lap])
def get_laps(driver_id: str, db: Session = Depends(get_db)):
    driver = db.query(DriverDB).filter(DriverDB.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver.laps

@app.get("/drivers/{driver_id}/laps/{lap_id}", response_model=Lap)
def get_lap(driver_id: str, lap_id: str, db: Session = Depends(get_db)):
    lap = db.query(LapDB).filter(LapDB.id == lap_id, LapDB.driver_id == driver_id).first()
    if not lap:
        raise HTTPException(status_code=404, detail="Lap not found")
    return lap

@app.put("/drivers/{driver_id}/laps/{lap_id}", response_model=Lap)
def update_lap(driver_id: str, lap_id: str, lap_update: LapUpdate, db: Session = Depends(get_db)):
    lap = db.query(LapDB).filter(LapDB.id == lap_id, LapDB.driver_id == driver_id).first()
    if not lap:
        raise HTTPException(status_code=404, detail="Lap not found")
    lap.lap_time = lap_update.lap_time
    lap.track = lap_update.track
    db.commit()
    db.refresh(lap)
    return lap

@app.delete("/drivers/{driver_id}/laps/{lap_id}")
def delete_lap(driver_id: str, lap_id: str, db: Session = Depends(get_db)):
    lap = db.query(LapDB).filter(LapDB.id == lap_id, LapDB.driver_id == driver_id).first()
    if not lap:
        raise HTTPException(status_code=404, detail="Lap not found")
    db.delete(lap)
    db.commit()
    return {"detail": "Lap deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)