"""Unit tests for CRM domain entities.

Tests business logic, validation, and domain rules.
"""

import pytest
from datetime import UTC, datetime
from uuid import UUID, uuid4

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
from src.crm.domain.value_objects import (
    ActivityStatus,
    ActivityType,
    DealStatus,
    Email,
    Money,
    PhoneNumber,
)


# ============================================================================
# Tag Entity Tests
# ============================================================================

class TestTagEntity:
    """Test Tag entity."""

    def test_create_tag_with_valid_data(self):
        """Test creating a tag with valid data."""
        tag = Tag.create(
            account_id=uuid4(),
            name="VIP Customer",
            color="#FF5733",
        )

        assert isinstance(tag.id, UUID)
        assert tag.name == "VIP Customer"
        assert tag.color == "#FF5733"

    def test_create_tag_with_long_name_raises_error(self):
        """Test creating a tag with name > 50 characters raises error."""
        with pytest.raises(TagValidationError, match="Tag name must be"):
            Tag.create(
                account_id=uuid4(),
                name="X" * 51,  # Exceeds 50 character limit
            )

    def test_create_tag_with_empty_name_raises_error(self):
        """Test creating a tag with empty name raises error."""
        with pytest.raises(TagValidationError, match="Tag name is required"):
            Tag.create(
                account_id=uuid4(),
                name="   ",  # Whitespace only
            )


# ============================================================================
# Contact Entity Tests
# ============================================================================

class TestContactEntity:
    """Test Contact entity."""

    def test_create_contact_with_valid_data(self):
        """Test creating a contact with valid data."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+14155551234",
            created_by=uuid4(),
        )

        assert isinstance(contact.id, UUID)
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert str(contact.email) == "john@example.com"
        assert contact.phone.formatted() == "+1 4155551234"

    def test_contact_full_name_property(self):
        """Test contact full_name property."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="Doe",
        )

        assert contact.full_name == "John Doe"

    def test_contact_full_name_without_last_name(self):
        """Test contact full_name with only first name."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="",
        )

        assert contact.full_name == "John"

    def test_create_contact_with_invalid_email_raises_error(self):
        """Test creating contact with invalid email raises error."""
        with pytest.raises(InvalidEmailError):
            Contact.create(
                account_id=uuid4(),
                first_name="John",
                last_name="Doe",
                email="invalid-email",  # Invalid format
            )

    def test_create_contact_with_invalid_phone_raises_error(self):
        """Test creating contact with invalid phone raises error."""
        with pytest.raises(InvalidPhoneNumberError):
            Contact.create(
                account_id=uuid4(),
                first_name="John",
                last_name="Doe",
                phone="123",  # Too short
            )

    def test_update_contact_fields(self):
        """Test updating contact fields."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="Doe",
        )

        contact.update(
            first_name="Jane",
            email="jane@example.com",
        )

        assert contact.first_name == "Jane"
        assert str(contact.email) == "jane@example.com"

    def test_add_tag_to_contact(self):
        """Test adding a tag to a contact."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="Doe",
        )

        tag = Tag.create(
            account_id=contact.account_id,
            name="VIP",
        )

        contact.add_tag(tag)

        assert len(contact.tags) == 1
        assert contact.tags[0].name == "VIP"

    def test_remove_tag_from_contact(self):
        """Test removing a tag from a contact."""
        contact = Contact.create(
            account_id=uuid4(),
            first_name="John",
            last_name="Doe",
        )

        tag = Tag.create(
            account_id=contact.account_id,
            name="VIP",
        )

        contact.add_tag(tag)
        assert len(contact.tags) == 1

        contact.remove_tag(tag.id)
        assert len(contact.tags) == 0


# ============================================================================
# Company Entity Tests
# ============================================================================

class TestCompanyEntity:
    """Test Company entity."""

    def test_create_company_with_valid_data(self):
        """Test creating a company with valid data."""
        company = Company.create(
            account_id=uuid4(),
            name="Acme Corporation",
            domain="acme.com",
            industry="Technology",
        )

        assert isinstance(company.id, UUID)
        assert company.name == "Acme Corporation"
        assert company.domain == "acme.com"
        assert company.industry == "Technology"

    def test_create_company_with_lowercase_domain(self):
        """Test creating a company converts domain to lowercase."""
        company = Company.create(
            account_id=uuid4(),
            name="Acme",
            domain="AcMe.com",  # Mixed case
        )

        assert company.domain == "acme.com"  # Lowercased

    def test_create_company_with_empty_name_raises_error(self):
        """Test creating company with empty name raises error."""
        with pytest.raises(CompanyValidationError, match="Company name is required"):
            Company.create(
                account_id=uuid4(),
                name="   ",
            )


# ============================================================================
# Pipeline and Stage Tests
# ============================================================================

class TestPipelineEntity:
    """Test Pipeline entity."""

    def test_create_pipeline_with_stages(self):
        """Test creating a pipeline with stages."""
        pipeline = Pipeline.create(
            account_id=uuid4(),
            name="Sales Pipeline",
        )

        stage1 = PipelineStage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name="Prospect",
            order=1,
            probability=10,
        )

        stage2 = PipelineStage(
            id=uuid4(),
            pipeline_id=pipeline.id,
            name="Closed Won",
            order=2,
            probability=100,
        )

        pipeline.add_stage(stage1)
        pipeline.add_stage(stage2)

        assert len(pipeline.stages) == 2
        assert pipeline.stages[0].order == 1
        assert pipeline.stages[1].order == 2

    def test_add_stage_with_invalid_probability_raises_error(self):
        """Test adding stage with invalid probability raises error."""
        with pytest.raises(PipelineValidationError, match="Probability must be"):
            PipelineStage(
                id=uuid4(),
                pipeline_id=uuid4(),
                name="Invalid",
                order=1,
                probability=150,  # Invalid: > 100
            )


# ============================================================================
# Deal Entity Tests
# ============================================================================

class TestDealEntity:
    """Test Deal entity."""

    def test_create_deal_with_valid_data(self):
        """Test creating a deal with valid data."""
        deal = Deal.create(
            account_id=uuid4(),
            pipeline_id=uuid4(),
            stage_id=uuid4(),
            name="Enterprise Deal",
            value=50000.00,
            created_by=uuid4(),
        )

        assert deal.name == "Enterprise Deal"
        assert deal.value.amount == 5000000  # Stored as cents
        assert deal.value.to_decimal() == 50000.00
        assert deal.status == DealStatus.OPEN

    def test_move_deal_to_new_stage(self):
        """Test moving deal to new stage."""
        deal = Deal.create(
            account_id=uuid4(),
            pipeline_id=uuid4(),
            stage_id=uuid4(),
            name="Test Deal",
            value=10000.00,
        )

        new_stage_id = uuid4()
        deal.move_to_stage(new_stage_id, probability=75)

        assert deal.stage_id == new_stage_id
        assert deal.probability == 75

    def test_move_won_deal_raises_error(self):
        """Test moving won deal raises error."""
        deal = Deal.create(
            account_id=uuid4(),
            pipeline_id=uuid4(),
            stage_id=uuid4(),
            name="Test Deal",
            value=10000.00,
        )

        deal.win()

        with pytest.raises(InvalidStageTransitionError):
            deal.move_to_stage(uuid4())

    def test_win_deal(self):
        """Test marking deal as won."""
        deal = Deal.create(
            account_id=uuid4(),
            pipeline_id=uuid4(),
            stage_id=uuid4(),
            name="Test Deal",
            value=10000.00,
        )

        deal.win()

        assert deal.status == DealStatus.WON
        assert deal.probability == 100
        assert deal.actual_close_date is not None

    def test_lose_deal(self):
        """Test marking deal as lost."""
        deal = Deal.create(
            account_id=uuid4(),
            pipeline_id=uuid4(),
            stage_id=uuid4(),
            name="Test Deal",
            value=10000.00,
        )

        deal.lose()

        assert deal.status == DealStatus.LOST
        assert deal.probability == 0
        assert deal.actual_close_date is not None


# ============================================================================
# Activity Entity Tests
# ============================================================================

class TestActivityEntity:
    """Test Activity entity."""

    def test_create_activity_with_valid_data(self):
        """Test creating an activity with valid data."""
        activity = Activity.create(
            account_id=uuid4(),
            activity_type=ActivityType.MEETING,
            title="Product Demo",
            due_date=datetime.now(UTC),
            created_by=uuid4(),
        )

        assert activity.title == "Product Demo"
        assert activity.activity_type == ActivityType.MEETING
        assert activity.status == ActivityStatus.PENDING

    def test_start_activity(self):
        """Test starting an activity."""
        activity = Activity.create(
            account_id=uuid4(),
            activity_type=ActivityType.TASK,
            title="Follow up",
        )

        activity.start()

        assert activity.status == ActivityStatus.IN_PROGRESS

    def test_complete_activity(self):
        """Test completing an activity."""
        activity = Activity.create(
            account_id=uuid4(),
            activity_type=ActivityType.TASK,
            title="Follow up",
        )

        activity.complete()

        assert activity.status == ActivityStatus.COMPLETED
        assert activity.completed_at is not None

    def test_cancel_activity(self):
        """Test cancelling an activity."""
        activity = Activity.create(
            account_id=uuid4(),
            activity_type=ActivityType.TASK,
            title="Follow up",
        )

        activity.cancel()

        assert activity.status == ActivityStatus.CANCELLED


# ============================================================================
# Note Entity Tests
# ============================================================================

class TestNoteEntity:
    """Test Note entity."""

    def test_create_note_with_valid_data(self):
        """Test creating a note with valid data."""
        note = Note.create(
            account_id=uuid4(),
            content="Discussed budget approval",
            note_type="note",
            created_by=uuid4(),
        )

        assert note.content == "Discussed budget approval"
        assert note.note_type == "note"

    def test_create_note_with_too_long_content_raises_error(self):
        """Test creating note with content > 10,000 characters raises error."""
        with pytest.raises(NoteValidationError, match="Note content must be"):
            Note.create(
                account_id=uuid4(),
                content="X" * 10001,  # Exceeds limit
            )

    def test_update_note_content(self):
        """Test updating note content."""
        note = Note.create(
            account_id=uuid4(),
            content="Original content",
        )

        note.update("Updated content")

        assert note.content == "Updated content"


# ============================================================================
# Value Object Tests
# ============================================================================

class TestEmailValueObject:
    """Test Email value object."""

    def test_valid_email(self):
        """Test creating valid email."""
        email = Email("john@example.com")
        assert str(email) == "john@example.com"

    def test_email_converts_to_lowercase(self):
        """Test email is converted to lowercase."""
        email = Email("John@Example.COM")
        assert str(email) == "john@example.com"

    def test_invalid_email_raises_error(self):
        """Test invalid email raises error."""
        with pytest.raises(InvalidEmailError):
            Email("invalid-email")


class TestPhoneNumberValueObject:
    """Test PhoneNumber value object."""

    def test_valid_phone_number(self):
        """Test creating valid phone number."""
        phone = PhoneNumber("+14155551234")
        assert phone.number == "14155551234"

    def test_phone_number_formatting(self):
        """Test phone number formatting."""
        phone = PhoneNumber("+14155551234", country_code="+1")
        assert phone.formatted() == "+1 14155551234"

    def test_invalid_phone_number_raises_error(self):
        """Test invalid phone number raises error."""
        with pytest.raises(InvalidPhoneNumberError):
            PhoneNumber("123")  # Too short


class TestMoneyValueObject:
    """Test Money value object."""

    def test_create_money_from_cents(self):
        """Test creating money from cents."""
        money = Money(50000, "USD")  # 50000 cents = $500.00
        assert money.amount == 50000
        assert money.currency == "USD"
        assert money.to_decimal() == 500.00

    def test_create_money_from_decimal(self):
        """Test creating money from decimal."""
        money = Money.from_decimal(99.99, "USD")
        assert money.amount == 9999  # Rounded to cents
        assert money.to_decimal() == 99.99

    def test_negative_money_raises_error(self):
        """Test negative money raises error."""
        with pytest.raises(ValueError):
            Money(-100, "USD")
