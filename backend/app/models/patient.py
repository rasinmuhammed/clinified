"""
Patient model for healthcare records
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Patient(Base):
    """Patient model for healthcare records"""
    
    __tablename__ = "patients"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Patient identification
    patient_id = Column(String(50), unique=True, nullable=False, index=True)  # Internal ID
    abha_id = Column(String(100), nullable=True, index=True)  # ABDM Health ID
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # male, female, other, unknown
    
    # Contact information
    phone = Column(String(20), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Emergency contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    
    # Medical information
    blood_group = Column(String(10), nullable=True)  # A+, B+, O+, AB+, etc.
    height = Column(Integer, nullable=True)  # in cm
    weight = Column(Integer, nullable=True)  # in kg
    allergies = Column(JSON, default=[])  # List of allergies
    medical_history = Column(JSON, default=[])  # Medical history
    family_history = Column(JSON, default=[])  # Family medical history
    
    # Insurance information
    insurance_provider = Column(String(200), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_group_number = Column(String(100), nullable=True)
    
    # ABDM integration
    abdm_consent = Column(Boolean, default=False)
    abdm_consent_date = Column(DateTime(timezone=True), nullable=True)
    abdm_consent_version = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_deceased = Column(Boolean, default=False)
    date_of_death = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_visit = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    preferences = Column(JSON, default={})
    
    # Relationships
    encounters = relationship("Encounter", back_populates="patient")
    observations = relationship("Observation", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    documents = relationship("Document", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id={self.patient_id}, name={self.full_name})>"
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate patient's age"""
        today = datetime.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def bmi(self) -> float:
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    def to_fhir_patient(self) -> dict:
        """Convert to FHIR Patient resource"""
        return {
            "resourceType": "Patient",
            "id": str(self.id),
            "identifier": [
                {
                    "system": "https://clinified.com/patient",
                    "value": self.patient_id
                }
            ] + ([{"system": "https://abdm.gov.in/health-id", "value": self.abha_id}] if self.abha_id else []),
            "active": self.is_active and not self.is_deceased,
            "name": [
                {
                    "use": "official",
                    "text": self.full_name,
                    "family": self.last_name,
                    "given": [self.first_name] + ([self.middle_name] if self.middle_name else [])
                }
            ],
            "telecom": [
                {"system": "phone", "value": self.phone} if self.phone else None,
                {"system": "email", "value": self.email} if self.email else None
            ],
            "gender": self.gender,
            "birthDate": self.date_of_birth.isoformat(),
            "address": [
                {
                    "use": "home",
                    "text": self.address,
                    "city": self.city,
                    "state": self.state,
                    "postalCode": self.pincode,
                    "country": self.country
                }
            ] if self.address else [],
            "contact": [
                {
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                    "code": "C",
                                    "display": "Emergency Contact"
                                }
                            ]
                        }
                    ],
                    "name": {
                        "text": self.emergency_contact_name
                    },
                    "telecom": [
                        {
                            "system": "phone",
                            "value": self.emergency_contact_phone
                        }
                    ] if self.emergency_contact_phone else []
                }
            ] if self.emergency_contact_name else [],
            "extension": [
                {
                    "url": "https://clinified.com/extension/blood-group",
                    "valueString": self.blood_group
                } if self.blood_group else None,
                {
                    "url": "https://clinified.com/extension/allergies",
                    "valueString": ", ".join(self.allergies) if self.allergies else ""
                }
            ]
        } 