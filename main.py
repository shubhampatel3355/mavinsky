from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import urllib.request
import datetime
import secrets
import string

import models
import schemas
from database import engine, SessionLocal

# models.Base.metadata.create_all(bind=engine) # Disabled: Managed by Alembic now

# Property API with Document Repository
app = FastAPI(title="Property API", strict_slashes=False)

# Increase the maximum request size to 50MB for document uploads
# This is handled by uvicorn/starlette naturally, but we should be aware of it.

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "ok"}


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "operational", "message": "Property API is active"}


@app.post("/properties/", response_model=schemas.PropertyResponse, status_code=201)
def create_property(property: schemas.PropertyCreate, db: Session = Depends(get_db)):
    property_data = property.model_dump()
    print(f"DEBUG: Creating property with documents count: {len(property.documents)}")
    property_data["key_features"] = [f.model_dump() for f in property.key_features]
    
    db_property = models.Property(**property_data)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    # Auto-generate BGM identifier (now MAVI)
    db_property.bgm_id = f"MAVI-{db_property.id:04d}"
    db.commit()
    db.refresh(db_property)
    
    # Auto-register category if it doesn't exist
    existing_cat = db.query(models.Category).filter(models.Category.name == property.category).first()
    if not existing_cat:
        new_cat = models.Category(name=property.category)
        db.add(new_cat)
        db.commit()

    return db_property


@app.get("/properties/", response_model=List[schemas.PropertyResponse])
def get_properties(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return db.query(models.Property).offset(skip).limit(limit).all()


@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """ Returns all registered categories """
    return db.query(models.Category).all()


@app.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        return existing
    new_cat = models.Category(name=category.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return


@app.delete("/categories/by-name/{name}", status_code=204)
def delete_category_by_name(name: str, db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.name == name).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return


@app.put("/properties/{property_id}", response_model=schemas.PropertyResponse)
def update_property(
    property_id: int,
    property_data: schemas.PropertyCreate,
    db: Session = Depends(get_db),
):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    print(f"DEBUG: Updating property {property_id}")
    print(f"DEBUG: Documents received: {len(property_data.documents)}")
    
    update_data = property_data.model_dump()
    
    from sqlalchemy.orm.attributes import flag_modified
    
    # Explicitly handle JSONB fields to ensure SQLAlchemy detects changes
    for key, value in update_data.items():
        if key == "documents":
            print(f"DEBUG: Setting documents: {len(value) if value else 0} items")
        setattr(db_property, key, value)
    
    # Force SQLAlchemy to recognize the JSONB change
    flag_modified(db_property, "documents")
    flag_modified(db_property, "media_files")
    flag_modified(db_property, "key_features")
    flag_modified(db_property, "amenities")

    try:
        db.commit()
        db.refresh(db_property)
        print(f"DEBUG: Successfully saved property {property_id}")
        return db_property
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Error saving property: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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


# --- Share / Public Property Endpoints ---


@app.post("/share-link", response_model=schemas.ShareResponse)
def share_property(share_data: schemas.ShareRequest, db: Session = Depends(get_db)):
    """Generate a public shareable URL for a property using its BGM ID."""
    db_property = db.query(models.Property).filter(
        models.Property.id == share_data.property_id
    ).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    bgm_id = db_property.bgm_id or f"MAVI-{db_property.id:04d}"
    base_url = "http://localhost:5173"  # Will be replaced by env var in production
    share_url = f"{base_url}/property/{bgm_id}"

    return {"shareUrl": share_url, "shareId": bgm_id}


@app.get("/public/property/{bgm_id}")
def get_public_property(bgm_id: str, db: Session = Depends(get_db)):
    """Public endpoint: returns property data with all contact info stripped out."""
    db_property = db.query(models.Property).filter(
        models.Property.bgm_id == bgm_id
    ).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Build a safe public payload — NO contact fields
    return {
        "bgm_id": db_property.bgm_id,
        "title": db_property.title,
        "price": db_property.price,
        "category": db_property.category,
        "property_for": db_property.property_for,
        "sqft": db_property.sqft,
        "address": db_property.address,
        "city": db_property.city,
        "description": db_property.description,
        "amenities": db_property.amenities or [],
        "key_features": db_property.key_features or [],
        "media_files": db_property.media_files or [],
        # documents intentionally excluded (may contain private data)
    }

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
