"""
Use Case: Generate Export Report

Generates export reports in various formats (CSV, PDF, JSON)
for workflow analytics data.
"""

from datetime import date, datetime, timedelta
from uuid import UUID
import csv
import io

from ...domain.analytics import AnalyticsNotFoundException, ExportGenerationException
from ..analytics_dtos import (
    ExportRequestDTO,
    ExportResponseDTO,
    ExportStatusDTO,
)


class GenerateExportReportUseCase:
    """
    Use case for generating analytics export reports.

    Supports multiple export formats with configurable options.
    """

    def __init__(self, analytics_repository, export_service, storage_service):
        self.analytics_repository = analytics_repository
        self.export_service = export_service
        self.storage_service = storage_service

    async def execute(self, request: ExportRequestDTO) -> ExportResponseDTO:
        """
        Execute the use case to generate export report.

        Args:
            request: Export request parameters

        Returns:
            ExportResponseDTO with download information

        Raises:
            AnalyticsNotFoundException: If workflow not found
            ExportGenerationException: If export generation fails
        """
        # Validate workflow exists
        workflow = await self.analytics_repository.get_workflow(request.workflow_id)
        if not workflow:
            raise AnalyticsNotFoundException(
                f"Workflow {request.workflow_id} not found",
                workflow_id=request.workflow_id,
            )

        # Fetch analytics data
        analytics_data = await self.analytics_repository.get_workflow_analytics(
            workflow_id=request.workflow_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # Generate export based on format
        try:
            if request.format == "csv":
                file_data = await self._generate_csv(analytics_data)
                content_type = "text/csv"
                file_extension = "csv"
            elif request.format == "json":
                file_data = await self._generate_json(analytics_data)
                content_type = "application/json"
                file_extension = "json"
            elif request.format == "pdf":
                file_data = await self._generate_pdf(analytics_data, request.include_charts)
                content_type = "application/pdf"
                file_extension = "pdf"
            else:
                raise ExportGenerationException(
                    f"Unsupported export format: {request.format}",
                    workflow_id=request.workflow_id,
                )

            # Store file
            export_id = UUID.uuid4()
            filename = f"workflow-analytics-{request.workflow_id}-{date.today()}.{file_extension}"
            download_url = await self.storage_service.store_file(
                export_id=export_id,
                filename=filename,
                file_data=file_data,
                content_type=content_type,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )

            return ExportResponseDTO(
                export_id=export_id,
                workflow_id=request.workflow_id,
                format=request.format,
                file_size_bytes=len(file_data),
                download_url=download_url,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )

        except Exception as e:
            raise ExportGenerationException(
                f"Failed to generate export: {str(e)}",
                workflow_id=request.workflow_id,
            )

    async def _generate_csv(self, analytics_data: dict) -> bytes:
        """Generate CSV export."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(["Metric", "Value"])

        # Write metrics
        for key, value in analytics_data.items():
            writer.writerow([key, value])

        return output.getvalue().encode('utf-8')

    async def _generate_json(self, analytics_data: dict) -> bytes:
        """Generate JSON export."""
        import json
        return json.dumps(analytics_data, indent=2, default=str).encode('utf-8')

    async def _generate_pdf(self, analytics_data: dict, include_charts: bool) -> bytes:
        """Generate PDF export."""
        # PDF generation would use reportlab or similar
        # For now, return placeholder
        return b"PDF export data (requires reportlab integration)"

    async def get_export_status(self, export_id: UUID) -> ExportStatusDTO:
        """Get status of export job."""
        status = await self.export_service.get_status(export_id)

        return ExportStatusDTO(
            export_id=export_id,
            status=status["status"],
            progress_percent=status.get("progress_percent", 0),
            download_url=status.get("download_url"),
            error_message=status.get("error_message"),
        )
