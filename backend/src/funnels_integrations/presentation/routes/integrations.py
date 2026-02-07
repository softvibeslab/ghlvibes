"""
Integrations API routes - SPEC-FUN-005.
14 endpoints for third-party integrations.
"""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.core.dependencies import get_db, get_current_account
from src.funnels_integrations.application.use_cases import (
    CreateEmailIntegrationUseCase,
    ListIntegrationsUseCase,
    GetIntegrationUseCase,
    UpdateIntegrationUseCase,
    DeleteIntegrationUseCase,
    TestIntegrationConnectionUseCase,
    CreateSMSIntegrationUseCase,
    CreateWebhookUseCase,
    TriggerWebhookUseCase,
    ListWebhookDeliveriesUseCase,
    RedeliverWebhookUseCase,
    CreateTrackingIntegrationUseCase,
    GetTrackingPixelCodeUseCase,
    GetIntegrationUsageStatsUseCase,
)

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


class EmailIntegrationCreate(BaseModel):
    provider: str = Field(..., regex="^(mailchimp|sendgrid|activecampaign|convertkit|getresponse|aweber)$")
    name: str = Field(..., min_length=3, max_length=100)
    credentials: dict
    settings: dict = {}
    mappings: List[dict] = []


class SMSIntegrationCreate(BaseModel):
    provider: str = Field(..., regex="^(twilio|plivo|messagebird|bandwidth|telnyx)$")
    name: str = Field(..., min_length=3, max_length=100)
    credentials: dict
    settings: dict = {}


class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    events: List[str]
    url: str
    method: str = "POST"
    headers: List[dict] = []
    retry_config: dict = {}
    secret: str | None = None


class TrackingIntegrationCreate(BaseModel):
    provider: str = Field(..., regex="^(facebook|google_analytics|tiktok|pinterest|twitter)$")
    name: str = Field(..., min_length=3, max_length=100)
    credentials: dict
    settings: dict = {}


@router.post("/email")
async def create_email_integration(
    data: EmailIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create email marketing integration."""
    use_case = CreateEmailIntegrationUseCase(db)
    integration = await use_case.execute(account_id, data.dict())
    return integration


@router.get("")
async def list_integrations(
    provider: str | None = None,
    status: str | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """List integrations for account."""
    use_case = ListIntegrationsUseCase(db)
    return await use_case.execute(account_id, provider, status, type)


@router.get("/{integration_id}")
async def get_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get integration details."""
    use_case = GetIntegrationUseCase(db)
    integration = await use_case.execute(integration_id, account_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/{integration_id}")
async def update_integration(
    integration_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Update integration."""
    use_case = UpdateIntegrationUseCase(db)
    integration = await use_case.execute(integration_id, account_id, data)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.delete("/{integration_id}", status_code=204)
async def delete_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Delete integration."""
    use_case = DeleteIntegrationUseCase(db)
    success = await use_case.execute(integration_id, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")


@router.post("/{integration_id}/test")
async def test_integration_connection(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Test integration connection."""
    use_case = TestIntegrationConnectionUseCase(db)
    result = await use_case.execute(integration_id, account_id)
    if not result:
        raise HTTPException(status_code=404, detail="Integration not found")
    return result


@router.post("/sms")
async def create_sms_integration(
    data: SMSIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create SMS integration."""
    use_case = CreateSMSIntegrationUseCase(db)
    integration = await use_case.execute(account_id, data.dict())
    return integration


@router.post("/webhooks")
async def create_webhook(
    data: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create webhook integration."""
    use_case = CreateWebhookUseCase(db)
    webhook = await use_case.execute(account_id, data.dict())
    return webhook


@router.post("/webhooks/trigger")
async def trigger_webhook(
    webhook_id: UUID,
    event_type: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Manually trigger a webhook."""
    use_case = TriggerWebhookUseCase(db)
    result = await use_case.execute(webhook_id, account_id, event_type, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return result


@router.get("/webhooks/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: UUID,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """List webhook delivery history."""
    use_case = ListWebhookDeliveriesUseCase(db)
    return await use_case.execute(webhook_id, account_id, status, date_from, date_to, page, page_size)


@router.post("/webhooks/deliveries/{delivery_id}/redeliver")
async def redeliver_webhook(
    delivery_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Redeliver failed webhook."""
    use_case = RedeliverWebhookUseCase(db)
    result = await use_case.execute(delivery_id, account_id)
    if not result:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return result


@router.post("/tracking")
async def create_tracking_integration(
    data: TrackingIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Create tracking pixel integration."""
    use_case = CreateTrackingIntegrationUseCase(db)
    integration = await use_case.execute(account_id, data.dict())
    return integration


@router.get("/tracking/{integration_id}/code")
async def get_tracking_pixel_code(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get tracking pixel embed code."""
    use_case = GetTrackingPixelCodeUseCase(db)
    code = await use_case.execute(integration_id, account_id)
    if not code:
        raise HTTPException(status_code=404, detail="Integration not found")
    return code


@router.get("/{integration_id}/stats")
async def get_integration_usage_stats(
    integration_id: UUID,
    date_from: str,
    date_to: str,
    db: AsyncSession = Depends(get_db),
    account_id: UUID = Depends(get_current_account),
):
    """Get integration usage statistics."""
    use_case = GetIntegrationUsageStatsUseCase(db)
    stats = await use_case.execute(integration_id, account_id, date_from, date_to)
    if not stats:
        raise HTTPException(status_code=404, detail="Integration not found")
    return stats
