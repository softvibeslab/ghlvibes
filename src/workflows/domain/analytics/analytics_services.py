"""
Domain services for Workflow Analytics.

Domain services contain business logic that doesn't naturally
belong to a single entity or value object. They orchestrate
domain behavior across multiple aggregates.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from uuid import UUID

from .analytics_entities import (
    WorkflowAnalytics,
    WorkflowFunnelMetrics,
    WorkflowActionMetrics,
    MetricsSnapshot,
)
from .analytics_value_objects import (
    EnrollmentMetrics,
    CompletionMetrics,
    ConversionMetrics,
    FunnelStepData,
    TimeRange,
    EnrollmentSource,
    ExitReason,
)
from .analytics_exceptions import (
    InvalidTimeRangeException,
    MetricsCalculationException,
    FunnelAnalysisException,
)


class MetricsCalculationService:
    """
    Domain service for calculating workflow metrics.

    Handles the computation of enrollment, completion, and
    conversion metrics from raw execution data.
    """

    def calculate_enrollment_metrics(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        execution_data: List[Dict],
    ) -> EnrollmentMetrics:
        """
        Calculate enrollment metrics from execution data.

        Args:
            workflow_id: Workflow identifier
            time_range: Time period for calculation
            execution_data: Raw execution records

        Returns:
            EnrollmentMetrics value object

        Raises:
            MetricsCalculationException: If calculation fails
        """
        try:
            total_enrolled = len(execution_data)

            # Count active enrollments (those not completed/exited)
            currently_active = sum(
                1 for e in execution_data
                if e.get('status') in ['active', 'in_progress']
            )

            # Count new enrollments in time range
            new_enrollments = sum(
                1 for e in execution_data
                if time_range.start_date <= e.get('enrolled_at', datetime.min).date() <= time_range.end_date
            )

            # Breakdown by source
            source_counts: Dict[EnrollmentSource, int] = {
                EnrollmentSource.TRIGGER: 0,
                EnrollmentSource.BULK: 0,
                EnrollmentSource.API: 0,
                EnrollmentSource.MANUAL: 0,
            }

            for execution in execution_data:
                source_str = execution.get('enrollment_source', 'manual').lower()
                try:
                    source = EnrollmentSource(source_str)
                    source_counts[source] += 1
                except ValueError:
                    source_counts[EnrollmentSource.MANUAL] += 1

            # Calculate enrollment rate (new enrollments per day)
            days = time_range.days_in_range()
            enrollment_rate = (
                Decimal(new_enrollments) / Decimal(days) if days > 0 else Decimal('0')
            ).quantize(Decimal('0.01'))

            return EnrollmentMetrics(
                total_enrolled=total_enrolled,
                currently_active=currently_active,
                new_enrollments=new_enrollments,
                enrollment_sources=source_counts,
                enrollment_rate=enrollment_rate,
            )

        except Exception as e:
            raise MetricsCalculationException(
                f"Failed to calculate enrollment metrics: {str(e)}",
                workflow_id=workflow_id,
            )

    def calculate_completion_metrics(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        execution_data: List[Dict],
    ) -> CompletionMetrics:
        """
        Calculate completion metrics from execution data.

        Args:
            workflow_id: Workflow identifier
            time_range: Time period for calculation
            execution_data: Raw execution records

        Returns:
            CompletionMetrics value object

        Raises:
            MetricsCalculationException: If calculation fails
        """
        try:
            # Count completions
            completed = sum(
                1 for e in execution_data
                if e.get('status') in ['completed', 'goal_achieved']
            )

            # Calculate completion rate
            total = len(execution_data)
            completion_rate = (
                (Decimal(completed) / Decimal(total) * 100) if total > 0 else Decimal('0')
            ).quantize(Decimal('0.01'))

            # Calculate average duration
            durations = [
                (e.get('completed_at') - e.get('enrolled_at')).total_seconds()
                for e in execution_data
                if e.get('completed_at') and e.get('enrolled_at')
            ]
            average_duration = (
                int(sum(durations) / len(durations)) if durations else 0
            )

            # Exit reasons breakdown
            exit_reasons: Dict[ExitReason, int] = {
                ExitReason.COMPLETED: 0,
                ExitReason.GOAL_ACHIEVED: 0,
                ExitReason.REMOVED: 0,
                ExitReason.ERROR: 0,
                ExitReason.TIMEOUT: 0,
                ExitReason.UNSUBSCRIBED: 0,
            }

            for execution in execution_data:
                reason_str = execution.get('exit_reason', 'completed').lower()
                try:
                    reason = ExitReason(reason_str.replace(' ', '_'))
                    exit_reasons[reason] += 1
                except ValueError:
                    exit_reasons[ExitReason.COMPLETED] += 1

            return CompletionMetrics(
                completed=completed,
                completion_rate=completion_rate,
                average_duration_seconds=average_duration,
                exit_reasons=exit_reasons,
            )

        except Exception as e:
            raise MetricsCalculationException(
                f"Failed to calculate completion metrics: {str(e)}",
                workflow_id=workflow_id,
            )


class FunnelAnalysisService:
    """
    Domain service for analyzing workflow funnel performance.

    Identifies drop-off points, bottlenecks, and conversion rates
    through each step of the workflow.
    """

    def analyze_funnel(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        step_data: List[Dict],
        execution_data: List[Dict],
    ) -> WorkflowFunnelMetrics:
        """
        Perform funnel analysis on workflow steps.

        Args:
            workflow_id: Workflow identifier
            time_range: Analysis time period
            step_data: Workflow step configuration
            execution_data: Execution records with step progress

        Returns:
            WorkflowFunnelMetrics entity

        Raises:
            FunnelAnalysisException: If analysis fails
        """
        try:
            # Create funnel step data
            funnel_steps = self._calculate_step_metrics(
                workflow_id,
                step_data,
                execution_data,
            )

            # Calculate overall conversion rate
            overall_conversion = self._calculate_overall_conversion(funnel_steps)

            # Create funnel metrics entity
            funnel_metrics = WorkflowFunnelMetrics(
                workflow_id=workflow_id,
                time_range=time_range,
                funnel_steps=funnel_steps,
                overall_conversion_rate=overall_conversion,
            )

            # Identify bottlenecks
            funnel_metrics.identify_bottlenecks(threshold=Decimal('20.0'))

            return funnel_metrics

        except Exception as e:
            raise FunnelAnalysisException(
                f"Failed to analyze funnel: {str(e)}",
                workflow_id=workflow_id,
            )

    def _calculate_step_metrics(
        self,
        workflow_id: UUID,
        step_data: List[Dict],
        execution_data: List[Dict],
    ) -> List[FunnelStepData]:
        """Calculate metrics for each funnel step."""
        steps = []

        for step_config in sorted(step_data, key=lambda s: s.get('order', 0)):
            step_id = UUID(step_config['id'])
            step_name = step_config['name']
            step_order = step_config['order']

            # Count contacts who entered this step
            entered = sum(
                1 for e in execution_data
                if step_id in e.get('steps_entered', [])
            )

            # Count contacts who completed this step
            completed = sum(
                1 for e in execution_data
                if step_id in e.get('steps_completed', [])
            )

            # Calculate drop-offs
            dropped_off = entered - completed

            # Calculate conversion rate
            conversion_rate = (
                (Decimal(completed) / Decimal(entered) * 100) if entered > 0 else Decimal('0')
            ).quantize(Decimal('0.01'))

            # Calculate average time in step
            step_times = [
                e.get('step_times', {}).get(str(step_id), 0)
                for e in execution_data
                if str(step_id) in e.get('step_times', {})
            ]
            avg_time = int(sum(step_times) / len(step_times)) if step_times else 0

            steps.append(FunnelStepData(
                step_id=step_id,
                step_name=step_name,
                step_order=step_order,
                entered=entered,
                completed=completed,
                dropped_off=dropped_off,
                step_conversion_rate=conversion_rate,
                average_time_in_step_seconds=avg_time,
            ))

        return steps

    def _calculate_overall_conversion(self, funnel_steps: List[FunnelStepData]) -> Decimal:
        """Calculate overall funnel conversion rate."""
        if not funnel_steps:
            return Decimal('0.00')

        first_step = funnel_steps[0]
        last_step = funnel_steps[-1]

        if first_step.entered == 0:
            return Decimal('0.00')

        return (
            Decimal(last_step.completed) / Decimal(first_step.entered) * 100
        ).quantize(Decimal('0.01'))


class ConversionCalculationService:
    """
    Domain service for calculating conversion metrics.

    Tracks goal achievements and conversion rates for workflows.
    """

    def calculate_conversion_metrics(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        execution_data: List[Dict],
        goal_data: List[Dict],
    ) -> ConversionMetrics:
        """
        Calculate conversion metrics from goal achievement data.

        Args:
            workflow_id: Workflow identifier
            time_range: Time period for calculation
            execution_data: Execution records
            goal_data: Goal achievement records

        Returns:
            ConversionMetrics value object

        Raises:
            MetricsCalculationException: If calculation fails
        """
        try:
            # Count goal achievements
            goals_achieved = sum(
                1 for e in execution_data
                if e.get('status') == 'goal_achieved'
                and time_range.start_date <= e.get('goal_achieved_at', datetime.min).date() <= time_range.end_date
            )

            # Calculate conversion rate
            total = len(execution_data)
            conversion_rate = (
                (Decimal(goals_achieved) / Decimal(total) * 100) if total > 0 else Decimal('0')
            ).quantize(Decimal('0.01'))

            # Calculate average time to conversion
            conversion_times = [
                (e.get('goal_achieved_at') - e.get('enrolled_at')).total_seconds()
                for e in execution_data
                if e.get('goal_achieved_at') and e.get('enrolled_at')
            ]
            avg_time_to_conversion = int(sum(conversion_times) / len(conversion_times)) if conversion_times else 0

            # Breakdown by goal type
            goal_breakdown = {}
            for goal in goal_data:
                goal_type = goal.get('type', 'unknown')
                goal_breakdown[goal_type] = goal_breakdown.get(goal_type, 0) + 1

            return ConversionMetrics(
                goals_achieved=goals_achieved,
                conversion_rate=conversion_rate,
                average_time_to_conversion_seconds=avg_time_to_conversion,
                goal_breakdown=goal_breakdown,
            )

        except Exception as e:
            raise MetricsCalculationException(
                f"Failed to calculate conversion metrics: {str(e)}",
                workflow_id=workflow_id,
            )


class AnalyticsAggregationService:
    """
    Domain service for aggregating analytics data.

    Combines metrics from multiple sources and creates
    aggregated snapshots for performance optimization.
    """

    def aggregate_daily_metrics(
        self,
        workflow_id: UUID,
        aggregation_date: date,
        execution_records: List[Dict],
    ) -> MetricsSnapshot:
        """
        Aggregate execution records into daily metrics snapshot.

        Args:
            workflow_id: Workflow identifier
            aggregation_date: Date to aggregate for
            execution_records: Execution records for the day

        Returns:
            MetricsSnapshot entity
        """
        # Calculate metrics for the day
        metrics_data = {
            'total_enrolled': len(execution_records),
            'new_enrollments': len(execution_records),
            'completed': sum(1 for e in execution_records if e.get('status') == 'completed'),
            'goals_achieved': sum(1 for e in execution_records if e.get('status') == 'goal_achieved'),
        }

        return MetricsSnapshot(
            workflow_id=workflow_id,
            snapshot_date=aggregation_date,
            snapshot_timestamp=datetime.utcnow(),
            metrics_data=metrics_data,
        )

    def aggregate_period_metrics(
        self,
        workflow_id: UUID,
        time_range: TimeRange,
        daily_snapshots: List[MetricsSnapshot],
    ) -> WorkflowAnalytics:
        """
        Aggregate daily snapshots into period metrics.

        Args:
            workflow_id: Workflow identifier
            time_range: Time period
            daily_snapshots: Daily metric snapshots

        Returns:
            WorkflowAnalytics aggregate
        """
        # Sum metrics across all snapshots
        total_enrolled = sum(
            s.metrics_data.get('total_enrolled', 0)
            for s in daily_snapshots
        )
        completed = sum(
            s.metrics_data.get('completed', 0)
            for s in daily_snapshots
        )
        goals_achieved = sum(
            s.metrics_data.get('goals_achieved', 0)
            for s in daily_snapshots
        )

        return WorkflowAnalytics(
            workflow_id=workflow_id,
            time_range=time_range,
        )
