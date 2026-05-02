# Backend/app/db/schema.py
from __future__ import annotations
 
import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
 
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
 
 
# ============================================================
# Base / Helpers
# ============================================================
 
 
class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""
 
 
def new_id() -> str:
    return str(uuid.uuid4())
 
 
def utcnow() -> datetime:
    return datetime.now(timezone.utc)
 
 
def enum_type(enum_cls: type[enum.Enum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda members: [member.value for member in members],
    )
 
 
class UUIDPKMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
 
 
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )
 
 
# ============================================================
# ENUMS
# ============================================================
 
 
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OWNER = "owner"
    DRIVER = "driver"
 
 
class OTPPurpose(str, enum.Enum):
    LOGIN = "login"
    SIGNUP = "signup"
    RESET_PASSWORD = "reset_password"
 
 
class UserLifecycleStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"
 
 
class OwnerVerificationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
 
 
class DriverVerificationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
 
 
class OwnerLifecycleStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"
 
 
class BikeStatus(str, enum.Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
 
 
class BikeVerificationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
 
 
class BikeOwnershipType(str, enum.Enum):
    SELF = "self"
    LEASED = "leased"
    FINANCED = "financed"
 
 
class FuelType(str, enum.Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    CNG = "cng"
 
 
class AssignmentStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"
    SUSPENDED = "suspended"
 
 
class RentalCollectionStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
 
 
class DepositTxnType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
 
 
class MaintenanceExpenseBearer(str, enum.Enum):
    OWNER = "owner"
    DRIVER = "driver"
    PLATFORM = "platform"
 
 
class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REVERSED = "reversed"
    HOLD = "hold"
 
 
class SupportStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    REJECTED = "rejected"
 
 
class AuditActorType(str, enum.Enum):
    ADMIN = "admin"
    SYSTEM = "system"
 
 
class OutboxStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
 
 
# ============================================================
# AUTH / USERS
# ============================================================
 
 
class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"
 
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        enum_type(UserRole, "user_role"), nullable=False
    )
    lifecycle_status: Mapped[UserLifecycleStatus] = mapped_column(
        enum_type(UserLifecycleStatus, "user_lifecycle_status"),
        nullable=False,
        default=UserLifecycleStatus.ACTIVE,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
 
    owner_profile: Mapped["OwnerProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="OwnerProfile.user_id",
    )
    driver_profile: Mapped["DriverProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="DriverProfile.user_id",
    )
 
    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["UserNotification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
 
    owned_bikes: Mapped[list["Bike"]] = relationship(
        back_populates="owner", foreign_keys="Bike.owner_user_id"
    )
    driver_assignments: Mapped[list["DriverBikeAssignment"]] = relationship(
        back_populates="driver", foreign_keys="DriverBikeAssignment.driver_user_id"
    )
    owner_assignments: Mapped[list["DriverBikeAssignment"]] = relationship(
        back_populates="owner", foreign_keys="DriverBikeAssignment.owner_user_id"
    )
 
    __table_args__ = (
        CheckConstraint("email <> ''", name="ck_users_email_nonempty"),
        CheckConstraint("phone <> ''", name="ck_users_phone_nonempty"),
    )
 
 
class OTPRequest(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "otp_requests"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    otp_code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    purpose: Mapped[OTPPurpose] = mapped_column(
        enum_type(OTPPurpose, "otp_purpose"),
        nullable=False,
        default=OTPPurpose.LOGIN,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    __table_args__ = (
        Index("ix_otp_requests_email_expires", "email", "expires_at"),
    )
 
 
class UserSession(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "user_sessions"
 
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
 
    user: Mapped["User"] = relationship(back_populates="sessions")
 
    __table_args__ = (Index("ix_user_sessions_user_expires", "user_id", "expires_at"),)
 
 
# ============================================================
# OWNER / DRIVER PROFILE
# ============================================================
 
 
class OwnerProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "owner_profiles"
 
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
 
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    profile_picture_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
 
    business_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
 
    aadhaar_number: Mapped[str | None] = mapped_column(String(12), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
 
    aadhaar_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pan_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
 
    bank_account_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    passbook_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
 
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
 
    verification_status: Mapped[OwnerVerificationStatus] = mapped_column(
        enum_type(OwnerVerificationStatus, "owner_verification_status"),
        nullable=False,
        default=OwnerVerificationStatus.DRAFT,
    )
    lifecycle_status: Mapped[OwnerLifecycleStatus] = mapped_column(
        enum_type(OwnerLifecycleStatus, "owner_lifecycle_status"),
        nullable=False,
        default=OwnerLifecycleStatus.ACTIVE,
    )
 
    verification_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_admin_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    user: Mapped["User"] = relationship(
        back_populates="owner_profile", foreign_keys=[user_id]
    )
 
    __table_args__ = (
        CheckConstraint("full_name <> ''", name="ck_owner_profiles_full_name_nonempty"),
        CheckConstraint("phone <> ''", name="ck_owner_profiles_phone_nonempty"),
    )
 
 
class DriverProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "driver_profiles"
 
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    driving_license_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    aadhaar_number: Mapped[str | None] = mapped_column(String(12), nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
 
    verification_status: Mapped[DriverVerificationStatus] = mapped_column(
        enum_type(DriverVerificationStatus, "driver_verification_status"),
        nullable=False,
        default=DriverVerificationStatus.DRAFT,
    )
    verification_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    user: Mapped["User"] = relationship(
        back_populates="driver_profile", foreign_keys=[user_id]
    )
 
    __table_args__ = (
        CheckConstraint("full_name <> ''", name="ck_driver_profiles_full_name_nonempty"),
    )
 
 
# ============================================================
# BIKES
# ============================================================
 
 
class Bike(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "bikes"
 
    owner_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
 
    bike_name: Mapped[str] = mapped_column(String(120), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
 
    fuel_type: Mapped[FuelType] = mapped_column(enum_type(FuelType, "fuel_type"), nullable=False)
    ownership_type: Mapped[BikeOwnershipType] = mapped_column(
        enum_type(BikeOwnershipType, "bike_ownership_type"), nullable=False
    )
 
    engine_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    chassis_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
 
    km_driven: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    year_of_purchase: Mapped[int | None] = mapped_column(Integer, nullable=True)
 
    status: Mapped[BikeStatus] = mapped_column(
        enum_type(BikeStatus, "bike_status"),
        nullable=False,
        default=BikeStatus.AVAILABLE,
    )
    verification_status: Mapped[BikeVerificationStatus] = mapped_column(
        enum_type(BikeVerificationStatus, "bike_verification_status"),
        nullable=False,
        default=BikeVerificationStatus.DRAFT,
    )
 
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
 
    owner: Mapped["User"] = relationship(back_populates="owned_bikes", foreign_keys=[owner_user_id])
    documents: Mapped[list["BikeDocument"]] = relationship(back_populates="bike", cascade="all, delete-orphan")
    images: Mapped[list["BikeImage"]] = relationship(back_populates="bike", cascade="all, delete-orphan")
    pricing: Mapped["BikePricing | None"] = relationship(back_populates="bike", uselist=False, cascade="all, delete-orphan")
    assignments: Mapped[list["DriverBikeAssignment"]] = relationship(back_populates="bike")
    maintenance_logs: Mapped[list["BikeMaintenanceLedger"]] = relationship(back_populates="bike")
 
    __table_args__ = (
        CheckConstraint("bike_name <> ''", name="ck_bikes_bike_name_nonempty"),
        CheckConstraint("brand <> ''", name="ck_bikes_brand_nonempty"),
        CheckConstraint("model <> ''", name="ck_bikes_model_nonempty"),
        CheckConstraint("registration_number <> ''", name="ck_bikes_reg_nonempty"),
        CheckConstraint("km_driven >= 0", name="ck_bikes_km_nonnegative"),
        Index("ix_bikes_owner_status", "owner_user_id", "status"),
    )
 
 
class BikeDocument(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "bike_documents"
 
    bike_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bikes.id", ondelete="CASCADE"), nullable=False
    )
    rc_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    insurance_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pollution_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    permit_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
 
    insurance_valid_till: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pollution_valid_till: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
 
    bike: Mapped["Bike"] = relationship(back_populates="documents")
 
    __table_args__ = (UniqueConstraint("bike_id", name="uq_bike_documents_bike"),)
 
 
class BikeImage(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "bike_images"
 
    bike_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bikes.id", ondelete="CASCADE"), nullable=False
    )
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    image_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
 
    bike: Mapped["Bike"] = relationship(back_populates="images")
 
    __table_args__ = (
        CheckConstraint("image_path <> ''", name="ck_bike_images_path_nonempty"),
        CheckConstraint("sort_order > 0", name="ck_bike_images_sort_positive"),
    )
 
 
class BikePricing(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "bike_pricing"
 
    bike_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bikes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    daily_rent: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weekly_rent: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    monthly_rent: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    security_deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    late_fee_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
 
    bike: Mapped["Bike"] = relationship(back_populates="pricing")
 
    __table_args__ = (
        CheckConstraint("daily_rent >= 0", name="ck_bike_pricing_daily_nonnegative"),
        CheckConstraint("security_deposit >= 0", name="ck_bike_pricing_deposit_nonnegative"),
        CheckConstraint("late_fee_per_day >= 0", name="ck_bike_pricing_late_fee_nonnegative"),
    )
 
 
# ============================================================
# ASSIGNMENT / LEDGER
# ============================================================
 
 
class DriverBikeAssignment(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "driver_bike_assignments"
 
    driver_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    owner_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    bike_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bikes.id", ondelete="RESTRICT"), nullable=False
    )
 
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
 
    daily_rent_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weekly_target_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    security_deposit_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
 
    status: Mapped[AssignmentStatus] = mapped_column(
        enum_type(AssignmentStatus, "assignment_status"),
        nullable=False,
        default=AssignmentStatus.ACTIVE,
    )
 
    ended_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    driver: Mapped["User"] = relationship(back_populates="driver_assignments", foreign_keys=[driver_user_id])
    owner: Mapped["User"] = relationship(back_populates="owner_assignments", foreign_keys=[owner_user_id])
    bike: Mapped["Bike"] = relationship(back_populates="assignments")
 
    rental_ledgers: Mapped[list["DriverRentalLedger"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")
    deposit_ledgers: Mapped[list["DriverSecurityDepositLedger"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")
    payout_ledgers: Mapped[list["OwnerPayoutLedger"]] = relationship(back_populates="assignment")
 
    __table_args__ = (
        CheckConstraint("daily_rent_amount >= 0", name="ck_driver_bike_assignments_daily_rent_nonnegative"),
        CheckConstraint("security_deposit_amount >= 0", name="ck_driver_bike_assignments_security_nonnegative"),
        Index("ix_driver_bike_assignments_driver_status", "driver_user_id", "status"),
        Index("ix_driver_bike_assignments_owner_status", "owner_user_id", "status"),
    )
 
 
class DriverRentalLedger(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "driver_rental_ledger"
 
    assignment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("driver_bike_assignments.id", ondelete="CASCADE"), nullable=False
    )
 
    rental_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rent_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    due_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
 
    collection_status: Mapped[RentalCollectionStatus] = mapped_column(
        enum_type(RentalCollectionStatus, "rental_collection_status"),
        nullable=False,
        default=RentalCollectionStatus.PENDING,
    )
 
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    assignment: Mapped["DriverBikeAssignment"] = relationship(back_populates="rental_ledgers")
 
    __table_args__ = (
        CheckConstraint("rent_amount >= 0", name="ck_driver_rental_ledger_rent_nonnegative"),
        CheckConstraint("amount_paid >= 0", name="ck_driver_rental_ledger_paid_nonnegative"),
        CheckConstraint("due_amount >= 0", name="ck_driver_rental_ledger_due_nonnegative"),
        Index("ix_driver_rental_ledger_assignment_date", "assignment_id", "rental_date"),
    )
 
 
class DriverSecurityDepositLedger(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "driver_security_deposit_ledger"
 
    assignment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("driver_bike_assignments.id", ondelete="CASCADE"), nullable=False
    )
 
    txn_type: Mapped[DepositTxnType] = mapped_column(
        enum_type(DepositTxnType, "deposit_txn_type"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    assignment: Mapped["DriverBikeAssignment"] = relationship(back_populates="deposit_ledgers")
 
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_driver_security_deposit_ledger_amount_positive"),
        Index("ix_driver_security_deposit_ledger_assignment", "assignment_id"),
    )
 
 
class BikeMaintenanceLedger(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "bike_maintenance_ledger"
 
    bike_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bikes.id", ondelete="CASCADE"), nullable=False
    )
 
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    expense_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    expense_bearer: Mapped[MaintenanceExpenseBearer] = mapped_column(
        enum_type(MaintenanceExpenseBearer, "maintenance_expense_bearer"),
        nullable=False,
    )
 
    service_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    bill_file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
 
    bike: Mapped["Bike"] = relationship(back_populates="maintenance_logs")
 
    __table_args__ = (
        CheckConstraint("title <> ''", name="ck_bike_maintenance_title_nonempty"),
        CheckConstraint("expense_amount >= 0", name="ck_bike_maintenance_amount_nonnegative"),
    )
 
 
class OwnerPayoutLedger(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "owner_payout_ledger"
 
    owner_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    assignment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("driver_bike_assignments.id", ondelete="SET NULL"), nullable=True
    )
 
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payout_status: Mapped[PayoutStatus] = mapped_column(
        enum_type(PayoutStatus, "payout_status"),
        nullable=False,
        default=PayoutStatus.PENDING,
    )
 
    payout_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    assignment: Mapped["DriverBikeAssignment | None"] = relationship(back_populates="payout_ledgers")
 
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_owner_payout_ledger_amount_nonnegative"),
        Index("ix_owner_payout_ledger_owner_status", "owner_user_id", "payout_status"),
    )
 
 
# ============================================================
# NOTIFICATIONS / SUPPORT / AUDIT / SYSTEM
# ============================================================
 
 
class UserNotification(UUIDPKMixin, Base):
    __tablename__ = "user_notifications"
 
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
 
    user: Mapped["User"] = relationship(back_populates="notifications")
 
 
class SupportTicket(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "support_tickets"
 
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SupportStatus] = mapped_column(
        enum_type(SupportStatus, "support_status"),
        nullable=False,
        default=SupportStatus.OPEN,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
 
    user: Mapped["User"] = relationship(back_populates="support_tickets")
 
 
class PlatformSettings(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_settings"
 
    settings_key: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, default="default")
    platform_commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("10.00"))
    late_fee_grace_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
 
    __table_args__ = (
        CheckConstraint(
            "platform_commission_percent >= 0 AND platform_commission_percent <= 100",
            name="ck_platform_settings_commission_range",
        ),
    )
 
 
class AdminAuditLog(UUIDPKMixin, Base):
    __tablename__ = "admin_audit_logs"
 
    actor_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_type: Mapped[AuditActorType] = mapped_column(
        enum_type(AuditActorType, "audit_actor_type"),
        nullable=False,
        default=AuditActorType.ADMIN,
    )
 
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
 
    before_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_json: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
 
    __table_args__ = (
        Index("ix_admin_audit_logs_actor", "actor_user_id"),
        Index("ix_admin_audit_logs_entity", "entity_type", "entity_id"),
    )
 
 
class OutboxEvent(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "outbox_events"
 
    event_name: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
 
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
 
    status: Mapped[OutboxStatus] = mapped_column(
        enum_type(OutboxStatus, "outbox_status"),
        nullable=False,
        default=OutboxStatus.PENDING,
    )
 
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    __table_args__ = (
        Index("ix_outbox_events_status_available", "status", "available_at"),
    )
 
 
class SystemConfigAudit(UUIDPKMixin, Base):
    __tablename__ = "system_config_audit"
 
    actor_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
 
    config_key: Mapped[str] = mapped_column(String(120), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
 
    __table_args__ = (
        Index("ix_system_config_audit_key", "config_key"),
    )
 
 
# ============================================================
# JOB LEASES (for cron / scheduler locking)
# ============================================================
 
 
class JobLease(Base):
    __tablename__ = "job_leases"
 
    job_name: Mapped[str] = mapped_column(String(120), primary_key=True, nullable=False)
    owner_id: Mapped[str] = mapped_column(String(120), nullable=False)
    lease_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )
 
    __table_args__ = (
        Index("ix_job_leases_lease_expires_at", "lease_expires_at"),
    )
 
