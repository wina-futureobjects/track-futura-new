import { apiFetch } from '../utils/api';

export interface DashboardStats {
  totalPosts: number;
  totalAccounts: number;
  totalReports: number;
  totalStorageUsed: string;
  creditBalance: number;
  maxCredits: number;
  engagementRate: number;
  growthRate: number;
  platforms: { [key: string]: any };
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  totalViews: number;
}

export interface ActivityTimelineItem {
  date: string;
  instagram: number;
  facebook: number;
  linkedin: number;
  tiktok: number;
}

export interface PlatformDistributionItem {
  name: string;
  value: number;
  color: string;
}

export interface RecentActivityItem {
  id: string;
  action: string;
  time: string;
  type: string;
}

export interface TopPerformerItem {
  platform: string;
  account: string;
  engagement: string;
  growth: string;
}

export interface WeeklyGoalItem {
  goal: string;
  current: number;
  target: number;
  percentage: number;
}

class DashboardService {
  async getStats(projectId?: string, daysBack: number = 30): Promise<DashboardStats> {
    try {
      const url = projectId
        ? `/api/dashboard/stats/${projectId}/?days_back=${daysBack}`
        : `/api/dashboard/stats/?days_back=${daysBack}`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch dashboard stats');
      return response.json();
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  async getActivityTimeline(projectId?: string, daysBack: number = 30): Promise<ActivityTimelineItem[]> {
    try {
      const url = projectId
        ? `/api/dashboard/activity-timeline/${projectId}/?days_back=${daysBack}`
        : `/api/dashboard/activity-timeline/?days_back=${daysBack}`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch activity timeline');
      return response.json();
    } catch (error) {
      console.error('Error fetching activity timeline:', error);
      throw error;
    }
  }

  async getPlatformDistribution(projectId?: string): Promise<PlatformDistributionItem[]> {
    try {
      const url = projectId
        ? `/api/dashboard/platform-distribution/${projectId}/`
        : `/api/dashboard/platform-distribution/`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch platform distribution');
      return response.json();
    } catch (error) {
      console.error('Error fetching platform distribution:', error);
      throw error;
    }
  }

  async getRecentActivity(projectId?: string, limit: number = 5): Promise<RecentActivityItem[]> {
    try {
      const url = projectId
        ? `/api/dashboard/recent-activity/${projectId}/?limit=${limit}`
        : `/api/dashboard/recent-activity/?limit=${limit}`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch recent activity');
      return response.json();
    } catch (error) {
      console.error('Error fetching recent activity:', error);
      throw error;
    }
  }

  async getTopPerformers(projectId?: string, limit: number = 3): Promise<TopPerformerItem[]> {
    try {
      const url = projectId
        ? `/api/dashboard/top-performers/${projectId}/?limit=${limit}`
        : `/api/dashboard/top-performers/?limit=${limit}`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch top performers');
      return response.json();
    } catch (error) {
      console.error('Error fetching top performers:', error);
      throw error;
    }
  }

  async getWeeklyGoals(projectId?: string): Promise<WeeklyGoalItem[]> {
    try {
      const url = projectId
        ? `/api/dashboard/weekly-goals/${projectId}/`
        : `/api/dashboard/weekly-goals/`;

      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Failed to fetch weekly goals');
      return response.json();
    } catch (error) {
      console.error('Error fetching weekly goals:', error);
      throw error;
    }
  }
}

export const dashboardService = new DashboardService();