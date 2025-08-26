"""
User model for authentication and authorization
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.core.database import Base

class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # User identification
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    
    # Professional information
    roles = Column(JSON, default=["staff"])  # ["doctor", "nurse", "admin", "staff"]
    specialization = Column(String(200), nullable=True)
    license_number = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    
    # ABDM integration
    abha_id = Column(String(100), nullable=True, index=True)
    hpr_id = Column(String(100), nullable=True, index=True)
    
    # Contact information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # MFA settings
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    
    # Account settings
    preferences = Column(JSON, default={})
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, roles={self.roles})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_doctor(self) -> bool:
        """Check if user is a doctor"""
        return "doctor" in self.roles
    
    @property
    def is_nurse(self) -> bool:
        """Check if user is a nurse"""
        return "nurse" in self.roles
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return "admin" in self.roles
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles
    
    def has_any_role(self, roles: list) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self.roles for role in roles) 