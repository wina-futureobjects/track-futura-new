import { getApiBaseUrl } from '../utils/api';

const API_BASE_URL = getApiBaseUrl();

export interface ApifyScraperRequest {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  platform: string;
  request_id: string;
  dataset_id?: string;
  created_at: string;
  completed_at?: string;
  batch_job?: number;
}

export interface ApifyBatchJob {
  id: number;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  project: number;
  created_at: string;
  completed_at?: string;
  total_requests: number;
  completed_requests: number;
  failed_requests: number;
}

export interface ApifyPollingStatus {
  is_polling: boolean;
  last_poll_time?: string;
  active_requests: number;
  polling_interval: number;
  next_poll_time?: string;
}

class ApifyMonitorService {
  private baseUrl = `${API_BASE_URL}/api/apify`;

  async getScraperRequests(limit = 20): Promise<ApifyScraperRequest[]> {
    try {
      const response = await fetch(`${this.baseUrl}/scraper-requests/?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to fetch scraper requests');
      const data = await response.json();
      return data.results || data;
    } catch (error) {
      console.error('Error fetching scraper requests:', error);
      throw error;
    }
  }

  async getBatchJobs(limit = 10): Promise<ApifyBatchJob[]> {
    try {
      const response = await fetch(`${this.baseUrl}/batch-jobs/?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to fetch batch jobs');
      const data = await response.json();
      return data.results || data;
    } catch (error) {
      console.error('Error fetching batch jobs:', error);
      throw error;
    }
  }

  async getPollingStatus(): Promise<ApifyPollingStatus> {
    // Since we don't have a direct polling status endpoint,
    // we'll simulate it based on recent activity
    try {
      const requests = await this.getScraperRequests(5);
      const activeRequests = requests.filter(r => 
        r.status === 'pending' || r.status === 'processing'
      );

      return {
        is_polling: true, // Assume polling is active if backend is running
        last_poll_time: new Date().toISOString(),
        active_requests: activeRequests.length,
        polling_interval: 30, // 30 seconds as configured
        next_poll_time: new Date(Date.now() + 30000).toISOString()
      };
    } catch (error) {
      return {
        is_polling: false,
        active_requests: 0,
        polling_interval: 30
      };
    }
  }

  async getStats() {
    try {
      const [requests, jobs] = await Promise.all([
        this.getScraperRequests(100),
        this.getBatchJobs(50)
      ]);

      const now = new Date();
      const last24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);

      const recent_requests = requests.filter(r => 
        new Date(r.created_at) > last24h
      );

      const stats = {
        total_requests: requests.length,
        active_requests: requests.filter(r => 
          r.status === 'pending' || r.status === 'processing'
        ).length,
        completed_requests: requests.filter(r => r.status === 'completed').length,
        failed_requests: requests.filter(r => r.status === 'failed').length,
        recent_requests_24h: recent_requests.length,
        total_batch_jobs: jobs.length,
        active_batch_jobs: jobs.filter(j => 
          j.status === 'pending' || j.status === 'processing'
        ).length,
        success_rate: requests.length > 0 ? 
          (requests.filter(r => r.status === 'completed').length / requests.length * 100) : 0,
      };

      return stats;
    } catch (error) {
      console.error('Error fetching Apify stats:', error);
      throw error;
    }
  }
}

export const apifyMonitorService = new ApifyMonitorService();
export default apifyMonitorService;