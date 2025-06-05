import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface WebhookMetrics {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate: number;
  error_rate: number;
  avg_response_time: number;
  max_response_time: number;
  min_response_time: number;
  last_success?: string;
  last_failure?: string;
}

export interface WebhookHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'critical';
  timestamp: string;
  metrics: WebhookMetrics;
  issues: string[];
  health_score: number;
}

export interface WebhookEvent {
  timestamp: string;
  event_id: string;
  event_type: string;
  status: string;
  response_time: number;
  payload_size: number;
  client_ip: string;
  user_agent: string;
  error_message?: string;
  metadata?: any;
}

export interface WebhookAlert {
  id: string;
  type: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
  resolved: boolean;
}

export interface WebhookAnalytics {
  total_events: number;
  success_rate: number;
  avg_response_time: number;
  hourly_breakdown: Array<{
    hour: string;
    total: number;
    success: number;
    errors: number;
    success_rate: number;
    avg_response_time: number;
  }>;
  error_types: Record<string, number>;
  top_clients: Array<{ ip: string; requests: number; success_rate: number }>;
  performance_trends: Array<{
    timestamp: string;
    response_time: number;
    success_rate: number;
  }>;
}

export interface WebhookTestResult {
  success: boolean;
  security_score: number;
  validation_results: {
    signature_valid: boolean;
    timestamp_valid: boolean;
    rate_limit_ok: boolean;
    ip_allowed: boolean;
    payload_valid: boolean;
  };
  response_time: number;
  error_message?: string;
}

export interface WebhookConfig {
  webhook_url: string;
  notify_url: string;
  webhook_token: string;
  rate_limit: number;
  allowed_ips: string[];
  max_timestamp_age: number;
}

class WebhookService {
  private baseUrl = `${API_BASE_URL}/api/brightdata`;

  async getMetrics(): Promise<WebhookMetrics> {
    try {
      const response: AxiosResponse<{ metrics: WebhookMetrics }> = await axios.get(
        `${this.baseUrl}/webhook/metrics/`
      );
      return response.data.metrics;
    } catch (error) {
      console.error('Failed to fetch webhook metrics:', error);
      throw this.handleError(error);
    }
  }

  async getHealth(): Promise<WebhookHealth> {
    try {
      const response: AxiosResponse<{ health: WebhookHealth }> = await axios.get(
        `${this.baseUrl}/webhook/health/`
      );
      return response.data.health;
    } catch (error) {
      console.error('Failed to fetch webhook health:', error);
      throw this.handleError(error);
    }
  }

  async getEvents(params?: {
    limit?: number;
    event_type?: string;
    status?: string;
    since?: string;
  }): Promise<WebhookEvent[]> {
    try {
      const response: AxiosResponse<{ events: WebhookEvent[] }> = await axios.get(
        `${this.baseUrl}/webhook/events/`,
        { params }
      );
      return response.data.events;
    } catch (error) {
      console.error('Failed to fetch webhook events:', error);
      throw this.handleError(error);
    }
  }

  async getAlerts(severity?: string): Promise<WebhookAlert[]> {
    try {
      const response: AxiosResponse<{ alerts: WebhookAlert[] }> = await axios.get(
        `${this.baseUrl}/webhook/alerts/`,
        { params: severity ? { severity } : {} }
      );
      return response.data.alerts;
    } catch (error) {
      console.error('Failed to fetch webhook alerts:', error);
      throw this.handleError(error);
    }
  }

  async getAnalytics(hours = 24): Promise<WebhookAnalytics> {
    try {
      const response: AxiosResponse<{ analytics: WebhookAnalytics }> = await axios.get(
        `${this.baseUrl}/webhook/analytics/`,
        { params: { hours } }
      );
      return response.data.analytics;
    } catch (error) {
      console.error('Failed to fetch webhook analytics:', error);
      throw this.handleError(error);
    }
  }

  async testWebhookSecurity(testData?: any): Promise<WebhookTestResult> {
    try {
      const response: AxiosResponse<WebhookTestResult> = await axios.post(
        `${this.baseUrl}/webhook/test/`,
        testData || { test: true, timestamp: Date.now() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to test webhook security:', error);
      throw this.handleError(error);
    }
  }

  async getConfiguration(): Promise<WebhookConfig> {
    try {
      const response: AxiosResponse<{ config: WebhookConfig }> = await axios.get(
        `${this.baseUrl}/webhook/config/`
      );
      return response.data.config;
    } catch (error) {
      console.error('Failed to fetch webhook configuration:', error);
      throw this.handleError(error);
    }
  }

  async updateConfiguration(config: Partial<WebhookConfig>): Promise<WebhookConfig> {
    try {
      const response: AxiosResponse<{ config: WebhookConfig }> = await axios.put(
        `${this.baseUrl}/webhook/config/`,
        config
      );
      return response.data.config;
    } catch (error) {
      console.error('Failed to update webhook configuration:', error);
      throw this.handleError(error);
    }
  }

  async resetMetrics(): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/webhook/reset-metrics/`);
    } catch (error) {
      console.error('Failed to reset webhook metrics:', error);
      throw this.handleError(error);
    }
  }

  async clearAlerts(): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/webhook/clear-alerts/`);
    } catch (error) {
      console.error('Failed to clear webhook alerts:', error);
      throw this.handleError(error);
    }
  }

  async exportEvents(format: 'csv' | 'json' = 'csv', params?: {
    start_date?: string;
    end_date?: string;
    event_type?: string;
    status?: string;
  }): Promise<Blob> {
    try {
      const response = await axios.get(
        `${this.baseUrl}/webhook/export-events/`,
        {
          params: { ...params, format },
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to export webhook events:', error);
      throw this.handleError(error);
    }
  }

  // Real-time webhook monitoring using Server-Sent Events
  createEventStream(onEvent: (event: WebhookEvent) => void, onError?: (error: any) => void): EventSource | null {
    try {
      const eventSource = new EventSource(`${this.baseUrl}/webhook/stream/`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onEvent(data);
        } catch (error) {
          console.error('Failed to parse webhook event:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('Webhook event stream error:', error);
        if (onError) onError(error);
      };

      return eventSource;
    } catch (error) {
      console.error('Failed to create webhook event stream:', error);
      if (onError) onError(error);
      return null;
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.response.data?.error || 'Server error';
      return new Error(`${message} (${error.response.status})`);
    } else if (error.request) {
      // Request failed to reach server
      return new Error('Network error: Unable to reach the server');
    } else {
      // Other error
      return new Error(error.message || 'Unknown error occurred');
    }
  }
}

export const webhookService = new WebhookService();
export default webhookService;
