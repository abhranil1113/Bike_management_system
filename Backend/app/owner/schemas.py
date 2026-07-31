# app/owner/schemas.py

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime


class OwnerProfileUpdate(BaseModel):
    business_name: Optional[str] = Field(None, example="GreenWheels Rental")
    aadhaar_number: Optional[str] = Field(None, min_length=12, max_length=12, example="123456789012")
    pan_number: Optional[str] = Field(None, min_length=10, max_length=10, example="ABCDE1234F")
    bank_account_name: Optional[str] = Field(None, example="John Doe")
    bank_account_number: Optional[str] = Field(None, example="987654321098")
    ifsc_code: Optional[str] = Field(None, example="SBIN0001234")
    address_line_1: Optional[str] = Field(None, example="123 Main Street")
    address_line_2: Optional[str] = Field(None, example="Suite 4B")
    city: Optional[str] = Field(None, example="Kolkata")
    state: Optional[str] = Field(None, example="West Bengal")
    postal_code: Optional[str] = Field(None, example="700001")


class BikeCreateRequest(BaseModel):
    bike_name: str = Field(..., example="Royal Enfield Classic 350")
    brand: str = Field(..., example="Royal Enfield")
    model: str = Field(..., example="Classic 350")
    registration_number: str = Field(..., example="WB02AB1234")
    color: Optional[str] = Field(None, example="Black")
    fuel_type: str = Field(..., example="petrol")  # petrol, diesel, electric, cng
    ownership_type: str = Field(..., example="self")  # self, leased, financed
    engine_number: Optional[str] = Field(None, example="ENG123456")
    chassis_number: Optional[str] = Field(None, example="CHS789012")
    km_driven: int = Field(0, ge=0, example=5000)
    year_of_purchase: Optional[int] = Field(None, example=2023)
    daily_rent: Decimal = Field(..., ge=0, example=500.00)
    weekly_rent: Optional[Decimal] = Field(None, ge=0, example=3000.00)
    monthly_rent: Optional[Decimal] = Field(None, ge=0, example=10000.00)
    security_deposit: Decimal = Field(..., ge=0, example=2000.00)
    late_fee_per_day: Decimal = Field(0.00, ge=0, example=100.00)


class BookingDecisionRequest(BaseModel):
    accepted: bool = Field(..., description="True to accept, False to reject")
    rejection_reason: Optional[str] = Field(None, description="Reason if rejected")


class ReturnBikeInspectionRequest(BaseModel):
    assignment_id: str = Field(..., description="Active bike assignment ID")
    is_damaged: bool = Field(..., description="True if bike has damage")
    damage_charge: Decimal = Field(Decimal("0.00"), ge=0, description="Amount charged for damage")
    notes: Optional[str] = Field(None, description="Inspection notes")
