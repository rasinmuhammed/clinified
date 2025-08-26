"""
Encounter model for clinical visits
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class Encounter(Base):
    """Encounter model for clinical visits"""
    
    __tablename__ = "encounters"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Relationships
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Encounter identification
    encounter_id = Column(String(50), unique=True, nullable=False, index=True)  # Internal ID
    fhir_encounter_id = Column(String(100), nullable=True, index=True)  # FHIR Encounter ID
    
    # Encounter details
    status = Column(String(20), default="planned")  # planned, arrived, triaged, in-progress, onleave, finished, cancelled
    class_code = Column(String(20), default="AMB")  # AMB, EMER, HH, IMP, ACUTE, NONAC, PRENC, SS, VR
    priority = Column(String(20), default="routine")  # routine, urgent, asap, stat
    
    # Timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Clinical information
    reason_code = Column(JSON, default=[])  # List of reason codes
    reason_text = Column(Text, nullable=True)
    diagnosis = Column(JSON, default=[])  # List of diagnoses
    chief_complaint = Column(Text, nullable=True)
    vital_signs = Column(JSON, default={})  # Vital signs data
    physical_examination = Column(Text, nullable=True)
    
    # Location and service
    location = Column(String(200), nullable=True)
    service_type = Column(String(100), nullable=True)  # Consultation, Follow-up, Emergency, etc.
    
    # Insurance and billing
    insurance_status = Column(String(50), nullable=True)  # covered, not-covered, pending
    copay_amount = Column(Integer, nullable=True)  # in paise
    total_amount = Column(Integer, nullable=True)  # in paise
    payment_status = Column(String(20), default="pending")  # pending, paid, waived
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # ABDM integration
    abdm_consent = Column(Boolean, default=False)
    abdm_consent_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional data
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    
    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    practitioner = relationship("User")
    observations = relationship("Observation", back_populates="encounter")
    medications = relationship("Medication", back_populates="encounter")
    documents = relationship("Document", back_populates="encounter")
    
    def __repr__(self):
        return f"<Encounter(id={self.id}, encounter_id={self.encounter_id}, patient={self.patient_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if encounter is currently active"""
        return self.status in ["arrived", "triaged", "in-progress"]
    
    @property
    def is_completed(self) -> bool:
        """Check if encounter is completed"""
        return self.status == "finished"
    
    @property
    def duration(self) -> int:
        """Calculate encounter duration in minutes"""
        if self.start_date and self.end_date:
            return int((self.end_date - self.start_date).total_seconds() / 60)
        return self.duration_minutes or 0
    
    def to_fhir_encounter(self) -> dict:
        """Convert to FHIR Encounter resource"""
        return {
            "resourceType": "Encounter",
            "id": str(self.id),
            "identifier": [
                {
                    "system": "https://clinified.com/encounter",
                    "value": self.encounter_id
                }
            ] + ([{"system": "https://clinified.com/fhir", "value": self.fhir_encounter_id}] if self.fhir_encounter_id else []),
            "status": self.status,
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": self.class_code,
                "display": self._get_class_display()
            },
            "priority": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                        "code": self.priority,
                        "display": self._get_priority_display()
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "participant": [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "ATND",
                                    "display": "attender"
                                }
                            ]
                        }
                    ],
                    "individual": {
                        "reference": f"Practitioner/{self.practitioner_id}"
                    }
                }
            ],
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat() if self.end_date else None
            },
            "reasonCode": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": code.get("code"),
                            "display": code.get("display")
                        }
                    ],
                    "text": code.get("text")
                }
                for code in self.reason_code
            ] if self.reason_code else [],
            "reasonReference": [
                {
                    "reference": f"Condition/{diagnosis.get('condition_id')}"
                }
                for diagnosis in self.diagnosis
            ] if self.diagnosis else [],
            "serviceProvider": {
                "reference": f"Organization/{self.tenant_id}"
            },
            "extension": [
                {
                    "url": "https://clinified.com/extension/chief-complaint",
                    "valueString": self.chief_complaint
                } if self.chief_complaint else None,
                {
                    "url": "https://clinified.com/extension/vital-signs",
                    "valueString": str(self.vital_signs)
                } if self.vital_signs else None,
                {
                    "url": "https://clinified.com/extension/payment-status",
                    "valueString": self.payment_status
                }
            ]
        }
    
    def _get_class_display(self) -> str:
        """Get display name for encounter class"""
        class_displays = {
            "AMB": "Ambulatory",
            "EMER": "Emergency",
            "HH": "Home Health",
            "IMP": "Inpatient Encounter",
            "ACUTE": "Inpatient Acute",
            "NONAC": "Inpatient Non-acute",
            "PRENC": "Pre-admission",
            "SS": "Short Stay",
            "VR": "Virtual"
        }
        return class_displays.get(self.class_code, self.class_code)
    
    def _get_priority_display(self) -> str:
        """Get display name for encounter priority"""
        priority_displays = {
            "routine": "Routine",
            "urgent": "Urgent",
            "asap": "ASAP",
            "stat": "Stat"
        }
        return priority_displays.get(self.priority, self.priority) 