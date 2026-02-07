"""Use case: Generate analytics export report.

This use case generates analytics reports in various formats (CSV, JSON, PDF)
for download by users.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from src.workflows.application.analytics_dtos import (
    ExportFormat,
    ExportRequestDTO,
    ExportResponseDTO,
)


class ExportStatus(StrEnum):
    """Status of export job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateExportReportUseCase:
    """Use case for generating analytics export reports.

    Orchestrates the generation of export files in various formats
    and manages download URLs.
    """

    def __init__(
        self,
        export_service: Any,  # Will be ExportGenerationService
        storage_service: Any,  # Will be FileStorageService
    ):
        """Initialize use case.

        Args:
            export_service: Service for generating export files.
            storage_service: Service for storing export files.
        """
        self.export_service = export_service
        self.storage_service = storage_service

    async def execute(self, request: ExportRequestDTO) -> ExportResponseDTO:
        """Generate export report.

        Args:
            request: Export request parameters.

        Returns:
            ExportResponseDTO with download information.

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist.
            ExportGenerationError: If export generation fails.
        """
        # Generate export ID
        export_id = uuid4()

        # Fetch analytics data
        analytics_data = await self.export_service.get_analytics_for_export(
            workflow_id=request.workflow_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # Generate export based on format
        export_content: Any
        content_type: str
        file_extension: str

        if request.format == ExportFormat.CSV:
            export_content, content_type, file_extension = (
                self._generate_csv_export(analytics_data)
            )
        elif request.format == ExportFormat.JSON:
            export_content, content_type, file_extension = (
                self._generate_json_export(analytics_data)
            )
        elif request.format == ExportFormat.PDF:
            export_content, content_type, file_extension = (
                await self._generate_pdf_export(
                    analytics_data,
                    include_charts=request.include_charts,
                )
            )
        else:
            raise ValueError(f"Unsupported export format: {request.format}")

        # Store export file
        filename = self._generate_filename(
            request.workflow_id,
            request.end_date,
            file_extension,
        )
        download_url = await self.storage_service.store_export(
            export_id=export_id,
            content=export_content,
            filename=filename,
            content_type=content_type,
        )

        # Calculate expiration (24 hours from now)
        expires_at = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        expires_at = expires_at.replace(day=expires_at.day + 1)

        return ExportResponseDTO(
            export_id=export_id,
            status=ExportStatus.COMPLETED,
            download_url=download_url,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )

    def _generate_csv_export(self, data: dict[str, Any]) -> tuple[str, str, str]:
        """Generate CSV export from analytics data.

        Args:
            data: Analytics data.

        Returns:
            Tuple of (csv_content, content_type, file_extension).
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "Date",
            "Total Enrolled",
            "New Enrollments",
            "Completed",
            "Completion Rate",
            "Goals Achieved",
            "Conversion Rate",
        ])

        # Write data rows
        for row in data.get("trends", []):
            writer.writerow([
                row["date"],
                row.get("total_enrolled", 0),
                row.get("new_enrollments", 0),
                row.get("completions", 0),
                row.get("completion_rate", 0.0),
                row.get("conversions", 0),
                row.get("conversion_rate", 0.0),
            ])

        csv_content = output.getvalue()
        return csv_content, "text/csv", "csv"

    def _generate_json_export(self, data: dict[str, Any]) -> tuple[str, str, str]:
        """Generate JSON export from analytics data.

        Args:
            data: Analytics data.

        Returns:
            Tuple of (json_content, content_type, file_extension).
        """
        import json

        json_content = json.dumps(data, indent=2, default=str)
        return json_content, "application/json", "json"

    async def _generate_pdf_export(
        self,
        data: dict[str, Any],
        include_charts: bool,
    ) -> tuple[bytes, str, str]:
        """Generate PDF export from analytics data.

        Args:
            data: Analytics data.
            include_charts: Whether to include visualizations.

        Returns:
            Tuple of (pdf_content, content_type, file_extension).

        Note:
            PDF generation requires additional dependencies (reportlab).
            This is a placeholder implementation.
        """
        # Placeholder: In production, use reportlab or similar
        # For now, return simple text-based PDF
        from io import BytesIO

        pdf_buffer = BytesIO()

        # Simple text-based PDF generation
        # In production, use reportlab properly
        text_content = f"""
Workflow Analytics Report
{'=' * 50}

Period: {data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}
Generated: {datetime.now(UTC).isoformat()}

Summary
-------
Total Enrolled: {data.get('summary', {}).get('total_enrolled', 0)}
Completed: {data.get('summary', {}).get('completed', 0)}
Goals Achieved: {data.get('summary', {}).get('goals_achieved', 0)}

Completion Rate: {data.get('summary', {}).get('completion_rate', 0.0)}%
Conversion Rate: {data.get('summary', {}).get('conversion_rate', 0.0)}%
"""

        pdf_buffer.write(text_content.encode("utf-8"))
        pdf_content = pdf_buffer.getvalue()

        return pdf_content, "application/pdf", "pdf"

    def _generate_filename(
        self,
        workflow_id: UUID,
        date: Any,
        extension: str,
    ) -> str:
        """Generate export filename.

        Args:
            workflow_id: Workflow identifier.
            date: Report date.
            extension: File extension.

        Returns:
            Generated filename.
        """
        date_str = date.isoformat() if hasattr(date, "isoformat") else str(date)
        return f"workflow-analytics-{workflow_id}-{date_str}.{extension}"
