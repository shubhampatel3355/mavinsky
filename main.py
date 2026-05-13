from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import urllib.request

import models
import schemas
from database import engine, SessionLocal

# models.Base.metadata.create_all(bind=engine) # Disabled: Managed by Alembic now

app = FastAPI(title="Property API")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://dashboard.mavinsky.com",
        "https://www.dashboard.mavinsky.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/properties/", response_model=schemas.PropertyResponse, status_code=201)
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db)):
    property_data = property.model_dump()
    property_data["key_features"] = [f.model_dump() for f in property.key_features]
    
    db_property = models.Property(**property_data)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    # Auto-generate BGM identifier
    db_property.bgm_id = f"BGM-{db_property.id:04d}"
    db.commit()
    db.refresh(db_property)
    
    return db_property


@app.get("/properties/", response_model=List[schemas.PropertyResponse])
def get_properties(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return db.query(models.Property).offset(skip).limit(limit).all()


@app.put("/properties/{property_id}", response_model=schemas.PropertyResponse)
def update_property(
    property_id: int,
    property_data: schemas.PropertyCreate,
    db: Session = Depends(get_db),
):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = property_data.model_dump(exclude_unset=True)
    if "key_features" in update_data:
        update_data["key_features"] = [f.model_dump() for f in property_data.key_features]

    for key, value in update_data.items():
        setattr(db_property, key, value)

    db.commit()
    db.refresh(db_property)
    return db_property


@app.get("/properties/{property_id}", response_model=schemas.PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


@app.delete("/properties/{property_id}", status_code=204)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")
        
    db.delete(db_property)
    db.commit()
    return


# --- Profile Endpoints ---


@app.get("/profile/", response_model=schemas.ProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == 1).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.put("/profile/", response_model=schemas.ProfileResponse)
def update_profile(profile_data: schemas.ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.id == 1).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile

# --- Utility Endpoints ---

@app.get("/resolve-url")
def resolve_url(url: str):
    """ Follows redirects like maps.app.goo.gl and returns the expanded URL for frontend map embedding securely """
    try:
        req = urllib.request.Request(
            url, 
            method="HEAD", 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            return {"expanded_url": response.url}
    except Exception as e:
        return {"expanded_url": url, "error": str(e)}
