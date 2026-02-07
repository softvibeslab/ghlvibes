'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CRMStatsGrid } from '@/components/crm/crm-stats-cards';
import { EmptyState } from '@/components/common/empty-state';
import { getCRMDashboardStats, getRecentActivities } from '@/lib/api/crm';
import { Users, Building2, Columns, CheckCircle, ArrowRight, Mail, Phone, Calendar } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

export default function CRMDashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['crm-dashboard-stats'],
    queryFn: getCRMDashboardStats,
  });

  const { data: recentActivities } = useQuery({
    queryKey: ['crm-recent-activities'],
    queryFn: () => getRecentActivities(5),
  });

  if (statsLoading) {
    return <div>Loading...</div>;
  }

  const quickActions = [
    {
      title: 'Add Contact',
      description: 'Create a new contact',
      icon: Users,
      href: '/crm/contacts?action=create',
      color: 'text-blue-600',
    },
    {
      title: 'Create Deal',
      description: 'Add to your pipeline',
      icon: Columns,
      href: '/crm/pipelines?action=create',
      color: 'text-green-600',
    },
    {
      title: 'Add Company',
      description: 'Create company account',
      icon: Building2,
      href: '/crm/companies?action=create',
      color: 'text-purple-600',
    },
    {
      title: 'New Task',
      description: 'Create task or reminder',
      icon: CheckCircle,
      href: '/crm/tasks?action=create',
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">CRM Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your Customer Relationship Management hub
        </p>
      </div>

      {/* Quick Stats */}
      {stats && (
        <CRMStatsGrid
          stats={[
            {
              title: 'Total Contacts',
              value: stats.contacts.total_contacts,
              icon: Users,
              trend: {
                value: 12,
                isPositive: true,
              },
            },
            {
              title: 'Active Deals',
              value: stats.deals.open_deals,
              icon: Columns,
              description: formatCurrency(stats.deals.total_value),
            },
            {
              title: 'Pipeline Value',
              value: formatCurrency(stats.revenue.pipeline_value),
              icon: Columns,
              trend: {
                value: 8,
                isPositive: true,
              },
            },
            {
              title: 'Today&apos;s Tasks',
              value: stats.tasks.today_count,
              icon: CheckCircle,
              description: `${stats.tasks.overdue_count} overdue`,
            },
          ]}
        />
      )}

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {quickActions.map((action) => (
          <Link key={action.title} href={action.href}>
            <Card className="transition-all hover:shadow-md cursor-pointer h-full">
              <CardHeader className="pb-3">
                <div className={`h-10 w-10 rounded-lg bg-muted flex items-center justify-center mb-2`}>
                  <action.icon className={`h-5 w-5 ${action.color}`} />
                </div>
                <CardTitle className="text-base">{action.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{action.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Activities */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Activities</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/crm/activities">
                View All
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {recentActivities && recentActivities.length > 0 ? (
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                      {activity.type === 'email' && <Mail className="h-4 w-4 text-blue-600" />}
                      {activity.type === 'call' && <Phone className="h-4 w-4 text-green-600" />}
                      {activity.type === 'meeting' && <Calendar className="h-4 w-4 text-purple-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.title}</p>
                      {activity.description && (
                        <p className="text-xs text-muted-foreground truncate">
                          {activity.description}
                        </p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        {activity.user_name} • {new Date(activity.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Calendar}
                title="No recent activities"
                description="Your recent activities will appear here"
              />
            )}
          </CardContent>
        </Card>

        {/* Quick Stats Details */}
        <Card>
          <CardHeader>
            <CardTitle>Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b">
                <span className="text-sm">New Contacts (This Month)</span>
                <span className="font-semibold">{stats?.contacts.new_this_month || 0}</span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b">
                <span className="text-sm">Conversion Rate</span>
                <span className="font-semibold">
                  {stats?.contacts.conversion_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b">
                <span className="text-sm">Won Deals (This Month)</span>
                <span className="font-semibold">
                  {formatCurrency(stats?.revenue.won_this_month || 0)}
                </span>
              </div>
              <div className="flex items-center justify-between pb-3 border-b">
                <span className="text-sm">Forecast (This Month)</span>
                <span className="font-semibold">
                  {formatCurrency(stats?.revenue.forecast_this_month || 0)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Tasks Completed (This Week)</span>
                <span className="font-semibold">{stats?.tasks.completed_this_week || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
