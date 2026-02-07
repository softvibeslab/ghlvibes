"""Domain layer for CRM module.

Contains domain entities, value objects, and business logic.
The domain layer is independent of infrastructure and presentation concerns.
"""

from src.crm.domain.entities import (
    Activity,
    Company,
    Contact,
    Deal,
    Note,
    Pipeline,
    PipelineStage,
    Tag,
)
from src.crm.domain.value_objects import (
    ActivityStatus,
    ActivityType,
    DealStatus,
    Email,
    Money,
    PhoneNumber,
)
from src.crm.domain.exceptions import (
    ActivityValidationError,
    CompanyValidationError,
    ContactValidationError,
    DealValidationError,
    InvalidEmailError,
    InvalidPhoneNumberError,
    InvalidStageTransitionError,
    NoteValidationError,
    PipelineValidationError,
)

__all__ = [
    # Entities
    "Activity",
    "Company",
    "Contact",
    "Deal",
    "Note",
    "Pipeline",
    "PipelineStage",
    "Tag",
    # Value Objects
    "ActivityStatus",
    "ActivityType",
    "DealStatus",
    "Email",
    "Money",
    "PhoneNumber",
    # Exceptions
    "ActivityValidationError",
    "CompanyValidationError",
    "ContactValidationError",
    "DealValidationError",
    "InvalidEmailError",
    "InvalidPhoneNumberError",
    "InvalidStageTransitionError",
    "NoteValidationError",
    "PipelineValidationError",
]
