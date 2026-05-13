from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    bgm_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, index=True)
    price = Column(String)
    category = Column(String)
    key_features = Column(JSONB)  # [{title: "x", value: "y"}]
    description = Column(Text)
    property_for = Column(String)  # 'Sale', 'Rent', 'Lease', 'Other'
    sqft = Column(String)

    # Location
    address = Column(String)
    city = Column(String)
    zip_code = Column(String)
    map_url = Column(String, nullable=True)

    # Media Links / Metadata
    media_files = Column(JSONB, default=list)  # List of dicts representing media files

    # Owner Info
    owner_name = Column(String, index=True)
    contact_number = Column(String)

    amenities = Column(JSONB, default=list)  # Store amenities as JSON array
    dynamic_fields = Column(
        JSONB, nullable=True, default=dict
    )  # Store dynamic properties

    # We can add a relationship to Profile if properties belong to users later
    # owner_id = Column(Integer, ForeignKey("profiles.id"))
    # owner = relationship("Profile", back_populates="properties")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    bio = Column(Text)
    profile_picture_url = Column(String)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
