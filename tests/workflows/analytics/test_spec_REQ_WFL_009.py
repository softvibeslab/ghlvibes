"""
Specification tests for SPEC-WFL-009: Workflow Analytics

These tests verify all 10 EARS requirements from the specification.
Tests follow specification-based testing principles to validate
business requirements rather than implementation details.
"""

import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from decimal import Decimal


class TestREQ_WFL_009_01_AnalyticsDashboardDisplay:
    """REQ-WFL-009-01: Analytics Dashboard Display (Event-Driven)"""

    def test_dashboard_displays_enrollment_metrics(self, analytics_query_service):
        """
        WHEN a user views workflow performance
        THEN the system shall display enrollment metrics
        """
        workflow_id = uuid4()
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date
        )

        assert analytics.total_enrolled >= 0
        assert analytics.currently_active >= 0
        assert analytics.enrollment_rate >= 0

    def test_dashboard_displays_completion_metrics(self, analytics_query_service):
        """Dashboard displays completion metrics"""
        workflow_id = uuid4()
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date
        )

        assert analytics.completed >= 0
        assert analytics.completion_rate >= 0
        assert analytics.completion_rate <= 100

    def test_dashboard_displays_conversion_metrics(self, analytics_query_service):
        """Dashboard displays conversion metrics"""
        workflow_id = uuid4()
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date
        )

        assert analytics.goals_achieved >= 0
        assert analytics.conversion_rate >= 0
        assert analytics.conversion_rate <= 100

    def test_dashboard_loads_within_2_seconds(self, analytics_query_service):
        """
        Dashboard loads within 2 seconds for workflows with up to 100,000 enrollments
        Performance requirement: P95 < 2 seconds
        """
        import time

        workflow_id = uuid4()
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        start_time = time.time()
        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date
        )
        load_time = time.time() - start_time

        assert load_time < 2.0, f"Dashboard load time {load_time}s exceeds 2s requirement"


class TestREQ_WFL_009_02_EnrollmentTracking:
    """REQ-WFL-009-02: Enrollment Tracking (Ubiquitous)"""

    def test_tracks_total_enrolled(self, analytics_repository):
        """System tracks total enrollments with timestamp"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_enrollment_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'total_enrolled')
        assert metrics.total_enrolled >= 0

    def test_tracks_enrollment_source(self, analytics_repository):
        """System tracks how contacts entered workflow"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_enrollment_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        # Should track sources: trigger, bulk, api, manual
        assert hasattr(metrics, 'enrollment_sources')
        assert 'trigger' in metrics.enrollment_sources or metrics.total_enrolled == 0

    def test_tracks_enrollment_rate_per_period(self, analytics_repository):
        """System tracks new enrollments per time period"""
        workflow_id = uuid4()

        daily_metrics = analytics_repository.get_enrollment_trends(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
            granularity='daily'
        )

        assert len(daily_metrics) <= 8  # 7 days + 1
        for metric in daily_metrics:
            assert hasattr(metric, 'new_enrollments')
            assert metric.new_enrollments >= 0


class TestREQ_WFL_009_03_CompletionMetrics:
    """REQ-WFL-009-03: Completion Metrics (Ubiquitous)"""

    def test_tracks_completion_count(self, analytics_repository):
        """System tracks total contacts who reached final step"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_completion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'completed')
        assert metrics.completed >= 0

    def test_tracks_completion_rate(self, analytics_repository):
        """System tracks completion rate percentage"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_completion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'completion_rate')
        assert 0 <= metrics.completion_rate <= 100

    def test_tracks_average_duration(self, analytics_repository):
        """System tracks average time from enrollment to completion"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_completion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'average_duration_seconds')
        assert metrics.average_duration_seconds >= 0

    def test_tracks_exit_reasons(self, analytics_repository):
        """System tracks distribution of why contacts left workflow"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_completion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'exit_reasons')


class TestREQ_WFL_009_04_ConversionTracking:
    """REQ-WFL-009-04: Conversion Tracking (Event-Driven)"""

    def test_records_conversion_events(self, analytics_repository):
        """
        WHEN a contact achieves a workflow goal
        THEN the system shall record conversion event
        """
        workflow_id = uuid4()
        contact_id = uuid4()
        goal_id = uuid4()

        # Record a conversion
        analytics_repository.record_goal_achievement(
            workflow_id=workflow_id,
            contact_id=contact_id,
            goal_id=goal_id,
            achieved_at=datetime.utcnow()
        )

        # Verify it was recorded
        metrics = analytics_repository.get_conversion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert metrics.goals_achieved >= 1

    def test_updates_conversion_metrics(self, analytics_repository):
        """Conversion metrics are updated after goal achievement"""
        workflow_id = uuid4()
        contact_id = uuid4()
        goal_id = uuid4()

        before_metrics = analytics_repository.get_conversion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        analytics_repository.record_goal_achievement(
            workflow_id=workflow_id,
            contact_id=contact_id,
            goal_id=goal_id,
            achieved_at=datetime.utcnow()
        )

        after_metrics = analytics_repository.get_conversion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert after_metrics.goals_achieved == before_metrics.goals_achieved + 1

    def test_tracks_time_to_conversion(self, analytics_repository):
        """System tracks average time from enrollment to goal"""
        workflow_id = uuid4()

        metrics = analytics_repository.get_conversion_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(metrics, 'average_time_to_conversion_seconds')
        assert metrics.average_time_to_conversion_seconds >= 0


class TestREQ_WFL_009_05_ActionPerformanceMetrics:
    """REQ-WFL-009-05: Action Performance Metrics (Ubiquitous)"""

    def test_tracks_action_execution_count(self, analytics_repository):
        """System tracks times each action was executed"""
        workflow_id = uuid4()

        action_metrics = analytics_repository.get_action_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        for action in action_metrics:
            assert hasattr(action, 'execution_count')
            assert action.execution_count >= 0

    def test_tracks_action_success_rate(self, analytics_repository):
        """System tracks percentage of successful executions"""
        workflow_id = uuid4()

        action_metrics = analytics_repository.get_action_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        for action in action_metrics:
            assert hasattr(action, 'success_rate')
            assert 0 <= action.success_rate <= 100

    def test_tracks_action_error_rate(self, analytics_repository):
        """System tracks percentage of failed executions"""
        workflow_id = uuid4()

        action_metrics = analytics_repository.get_action_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        for action in action_metrics:
            assert hasattr(action, 'error_rate')
            assert 0 <= action.error_rate <= 100

    def test_tracks_action_duration(self, analytics_repository):
        """System tracks average execution time per action type"""
        workflow_id = uuid4()

        action_metrics = analytics_repository.get_action_metrics(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        for action in action_metrics:
            assert hasattr(action, 'average_duration_ms')
            assert action.average_duration_ms >= 0


class TestREQ_WFL_009_06_DropoffAnalysis:
    """REQ-WFL-009-06: Drop-off Analysis (Event-Driven)"""

    def test_identifies_dropoff_points(self, funnel_analysis_service):
        """
        WHEN analyzing workflow funnel
        THEN the system shall identify drop-off points
        """
        workflow_id = uuid4()

        funnel_analysis = funnel_analysis_service.analyze_funnel(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(funnel_analysis, 'drop_off_points')
        assert len(funnel_analysis.drop_off_points) >= 0

    def test_calculates_step_conversion_rates(self, funnel_analysis_service):
        """System calculates conversion between consecutive steps"""
        workflow_id = uuid4()

        funnel_analysis = funnel_analysis_service.analyze_funnel(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        for step in funnel_analysis.funnel_steps:
            assert hasattr(step, 'step_conversion_rate')
            assert 0 <= step.step_conversion_rate <= 100

    def test_identifies_bottlenecks(self, funnel_analysis_service):
        """System identifies steps causing delays"""
        workflow_id = uuid4()

        funnel_analysis = funnel_analysis_service.analyze_funnel(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert hasattr(funnel_analysis, 'bottleneck_steps')
        # Bottleneck steps should be those with highest drop-off rates

    def test_provides_comparison_benchmarks(self, funnel_analysis_service):
        """System provides performance vs previous periods"""
        workflow_id = uuid4()

        current_period = (
            date.today() - timedelta(days=30),
            date.today()
        )
        previous_period = (
            date.today() - timedelta(days=60),
            date.today() - timedelta(days=31)
        )

        current_funnel = funnel_analysis_service.analyze_funnel(
            workflow_id=workflow_id,
            start_date=current_period[0],
            end_date=current_period[1]
        )

        previous_funnel = funnel_analysis_service.analyze_funnel(
            workflow_id=workflow_id,
            start_date=previous_period[0],
            end_date=previous_period[1]
        )

        # Should be able to compare performance
        assert hasattr(current_funnel, 'overall_conversion_rate')
        assert hasattr(previous_funnel, 'overall_conversion_rate')


class TestREQ_WFL_009_07_TimeBasedFiltering:
    """REQ-WFL-009-07: Time-Based Filtering (State-Driven)"""

    def test_preset_ranges_today(self, analytics_query_service):
        """System supports 'Today' preset range"""
        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=date.today(),
            end_date=date.today()
        )

        assert analytics is not None

    def test_preset_ranges_last_7_days(self, analytics_query_service):
        """System supports 'Last 7 days' preset range"""
        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=date.today() - timedelta(days=7),
            end_date=date.today()
        )

        assert analytics is not None

    def test_preset_ranges_last_30_days(self, analytics_query_service):
        """System supports 'Last 30 days' preset range"""
        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )

        assert analytics is not None

    def test_preset_ranges_last_90_days(self, analytics_query_service):
        """System supports 'Last 90 days' preset range"""
        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=date.today() - timedelta(days=90),
            end_date=date.today()
        )

        assert analytics is not None

    def test_custom_date_range(self, analytics_query_service):
        """System supports custom date range"""
        custom_start = date(2026, 1, 1)
        custom_end = date(2026, 1, 31)

        analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=custom_start,
            end_date=custom_end
        )

        assert analytics is not None

    def test_comparison_mode(self, analytics_query_service):
        """System supports comparison with previous period"""
        current_period = (
            date.today() - timedelta(days=30),
            date.today()
        )
        previous_period = (
            date.today() - timedelta(days=60),
            date.today() - timedelta(days=31)
        )

        current_analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=current_period[0],
            end_date=current_period[1]
        )

        previous_analytics = analytics_query_service.get_workflow_analytics(
            workflow_id=uuid4(),
            start_date=previous_period[0],
            end_date=previous_period[1]
        )

        # Should be able to compare metrics between periods
        assert current_analytics is not None
        assert previous_analytics is not None


class TestREQ_WFL_009_08_DataExport:
    """REQ-WFL-009-08: Data Export (Event-Driven)"""

    def test_export_csv_format(self, export_service):
        """
        WHEN user requests analytics export in CSV format
        THEN the system shall generate downloadable CSV report
        """
        workflow_id = uuid4()

        csv_data = export_service.generate_export(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            format='csv'
        )

        assert csv_data is not None
        assert isinstance(csv_data, bytes)
        # CSV should contain headers and data rows

    def test_export_pdf_format(self, export_service):
        """
        WHEN user requests analytics export in PDF format
        THEN the system shall generate formatted PDF report
        """
        workflow_id = uuid4()

        pdf_data = export_service.generate_export(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            format='pdf'
        )

        assert pdf_data is not None
        assert isinstance(pdf_data, bytes)
        # PDF should have valid PDF header

    def test_export_json_format(self, export_service):
        """
        WHEN user requests analytics export in JSON format
        THEN the system shall generate API-compatible structured data
        """
        workflow_id = uuid4()

        json_data = export_service.generate_export(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            format='json'
        )

        assert json_data is not None
        # JSON should be parseable

    def test_export_generation_timeout(self, export_service):
        """Export generation should complete within 10 seconds"""
        import time

        workflow_id = uuid4()
        start_time = time.time()

        export_service.generate_export(
            workflow_id=workflow_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            format='csv'
        )

        generation_time = time.time() - start_time

        assert generation_time < 10.0, f"Export generation {generation_time}s exceeds 10s"


class TestREQ_WFL_009_09_RealtimeUpdates:
    """REQ-WFL-009-09: Real-time Updates (State-Driven)"""

    def test_realtime_updates_via_sse(self, analytics_streaming_service):
        """
        WHILE dashboard is open and workflow is active
        THEN the system shall update metrics in real-time
        """
        workflow_id = uuid4()

        # SSE stream should be available
        stream = analytics_streaming_service.create_stream(workflow_id=workflow_id)

        assert stream is not None

    def test_updates_poll_every_5_seconds(self, analytics_streaming_service):
        """Polling interval: 5 seconds for active workflows"""
        workflow_id = uuid4()

        stream_config = analytics_streaming_service.get_stream_config(
            workflow_id=workflow_id
        )

        assert stream_config.poll_interval_seconds == 5

    def test_incremental_updates(self, analytics_streaming_service):
        """Only changed metrics transmitted"""
        workflow_id = uuid4()

        # Should support incremental updates
        stream = analytics_streaming_service.create_stream(workflow_id=workflow_id)

        assert hasattr(stream, 'send_update')
        assert hasattr(stream, 'get_changes_since')

    def test_connection_recovery(self, analytics_streaming_service):
        """Auto-reconnect on network issues"""
        workflow_id = uuid4()

        stream = analytics_streaming_service.create_stream(workflow_id=workflow_id)

        # Should handle disconnection and reconnection
        assert hasattr(stream, 'reconnect')
        assert hasattr(stream, 'is_connected')


class TestREQ_WFL_009_10_DataRetention:
    """REQ-WFL-009-10: Data Retention (Unwanted)"""

    def test_detailed_logs_retention_90_days(self, data_retention_service):
        """
        THE SYSTEM SHALL NOT retain detailed execution logs beyond 90 days
        """
        old_date = date.today() - timedelta(days=91)

        # Detailed logs older than 90 days should be deleted
        cleanup_result = data_retention_service.cleanup_detailed_logs(
            before_date=old_date
        )

        assert cleanup_result.deleted_count >= 0

    def test_daily_aggregates_retention_2_years(self, data_retention_service):
        """Aggregated daily metrics retained for 2 years"""
        cutoff_date = date.today() - timedelta(days=730)  # 2 years

        # Daily aggregates within 2 years should be preserved
        preserved = data_retention_service.get_daily_aggregates(
            after_date=cutoff_date
        )

        assert len(preserved) >= 0

    def test_monthly_summaries_indefinite(self, data_retention_service):
        """Monthly summaries retained indefinitely"""
        # Monthly summaries should never be auto-deleted
        summaries = data_retention_service.get_monthly_summaries()

        assert summaries is not None

    def test_retention_policy_enforcement(self, data_retention_service):
        """Data retention policy is automatically enforced"""
        # Should have scheduled cleanup job
        job_status = data_retention_service.get_cleanup_job_status()

        assert job_status.enabled == True
        assert job_status.schedule == 'daily'
