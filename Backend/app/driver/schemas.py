# app/driver/schemas.py

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


class DriverProfileUpdate(BaseModel):
    driving_license_number: Optional[str] = Field(None, min_length=5, max_length=30, example="DL-1420110012345")
    aadhaar_number: Optional[str] = Field(None, min_length=12, max_length=12, example="987654321098")
    pan_number: Optional[str] = Field(None, min_length=10, max_length=10, example="ABCDE1234F")
    address: Optional[str] = Field(None, example="123 Park Street, Kolkata, West Bengal")
    emergency_contact_name: Optional[str] = Field(None, example="Jane Doe")
    emergency_contact_phone: Optional[str] = Field(None, example="9876543210")


class BikeSearchQuery(BaseModel):
    city: Optional[str] = Field(None, example="Kolkata")
    brand: Optional[str] = Field(None, example="Royal Enfield")
    fuel_type: Optional[str] = Field(None, example="petrol")
    max_daily_rent: Optional[Decimal] = Field(None, ge=0, example=1000.00)


class CreateBookingRequest(BaseModel):
    bike_id: str = Field(..., description="Target bike ID")
    rental_hours: Optional[int] = Field(24, ge=1, description="Rental duration in hours (e.g. 1, 2, 4, 8, 12, 24)")
    payment_method: Optional[str] = Field("cod", description="'cod' for Cash on Delivery or 'razorpay' / 'upi'")
    message: Optional[str] = Field(None, example="Requesting for rental.")
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
