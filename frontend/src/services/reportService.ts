import { apiFetch } from '../utils/api';

export interface ReportTemplate {
  id: number;
  name: string;
  description: string;
  template_type: string;
  icon: string;
  color: string;
  estimated_time: string;
  required_data_types: string[];
  features: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GeneratedReport {
  id: number;
  title: string;
  template: number;
  template_name?: string;
  template_type?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  configuration: any;
  results: any;
  error_message?: string;
  data_source_count: number;
  processing_time?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

class ReportService {
  async getTemplates(): Promise<ReportTemplate[]> {
    try {
      const response = await apiFetch('/api/reports/templates/');
      if (!response.ok) throw new Error('Failed to fetch report templates');
      return response.json();
    } catch (error) {
      console.error('Error fetching report templates:', error);
      throw error;
    }
  }

  async getReports(): Promise<GeneratedReport[]> {
    try {
      const response = await apiFetch('/api/reports/generated/');
      if (!response.ok) throw new Error('Failed to fetch generated reports');
      return response.json();
    } catch (error) {
      console.error('Error fetching generated reports:', error);
      throw error;
    }
  }

  async getReport(id: number): Promise<GeneratedReport> {
    try {
      const response = await apiFetch(`/api/reports/generated/${id}/`);
      if (!response.ok) throw new Error('Failed to fetch report');
      return response.json();
    } catch (error) {
      console.error('Error fetching report:', error);
      throw error;
    }
  }

  async generateReport(templateId: number, title: string, configuration: any = {}, projectId?: string): Promise<GeneratedReport> {
    try {
      const body: any = {
        template_id: templateId,
        title: title,
        configuration: configuration
      };

      // Add project_id if available for real data analysis
      if (projectId) {
        body.project_id = projectId;
      }

      const response = await apiFetch('/api/reports/generated/generate_report/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });
      if (!response.ok) throw new Error('Failed to generate report');
      return response.json();
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }

  async downloadPDF(reportId: number): Promise<void> {
    try {
      const response = await apiFetch(`/api/reports/generated/${reportId}/download_pdf/`);

      if (!response.ok) throw new Error('Failed to download PDF');

      // Get the blob from response
      const blob = await response.blob();

      // Create blob link to download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Get filename from response headers or create one
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `report_${reportId}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  }

  async downloadCSV(reportId: number): Promise<void> {
    try {
      const response = await apiFetch(`/api/reports/generated/${reportId}/download_csv/`);

      if (!response.ok) throw new Error('Failed to download CSV');

      // Get the blob from response
      const blob = await response.blob();

      // Create blob link to download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Get filename from response headers or create one
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `report_${reportId}.csv`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      throw error;
    }
  }
}

export const reportService = new ReportService();