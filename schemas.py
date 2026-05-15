from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class KeyFeature(BaseModel):
    title: str
    value: str

class PropertyCreate(BaseModel):
    title: str
    price: str
    category: str
    key_features: List[KeyFeature]
    description: str
    property_for: Optional[str] = None
    sqft: Optional[str] = None
    address: str
    city: str
    zip_code: str
    map_url: Optional[str] = None
    media_files: List[Dict[str, Any]]
    owner_name: str
    contact_number: str
    amenities: List[str]
    dynamic_fields: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = []

class PropertyResponse(PropertyCreate):
    id: int
    bgm_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    bio: str
    profile_picture_url: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ShareRequest(BaseModel):
    property_id: int


class ShareResponse(BaseModel):
    shareUrl: str
    shareId: str
