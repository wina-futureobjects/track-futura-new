import { apiFetch } from '../utils/api';

export interface InputCollection {
  id: number;
  project: number;
  project_name: string;
  platform_service: number;
  platform_service_details: {
    platform: {
      id: number;
      name: string;
      display_name: string;
      is_enabled: boolean;
    };
    service: {
      id: number;
      name: string;
      display_name: string;
    };
    is_enabled: boolean;
  };
  platform_name: string;
  service_name: string;
  urls: string[];
  url_count: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTask {
  id: number;
  input_collection: number;
  input_collection_details: InputCollection;
  batch_job: number;
  batch_job_name: string;
  batch_job_status: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface PlatformService {
  id: number;
  platform: {
    id: number;
    name: string;
    display_name: string;
    is_enabled: boolean;
  };
  service: {
    id: number;
    name: string;
    display_name: string;
  };
  is_enabled: boolean;
  description: string;
}

export interface CreateInputCollectionRequest {
  project: number;
  platform_service: number;
  urls: string[];
}

export interface TrackSource {
  id: number;
  name: string;
  facebook_link: string | null;
  instagram_link: string | null;
  linkedin_link: string | null;
  tiktok_link: string | null;
  other_social_media: string | null;
  created_at: string;
  updated_at: string;
}

export interface TrackSourceCollection {
  id: number;
  name: string;
  platform_name: string;
  service_name: string;
  urls: string[];
  url_count: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  source_type: 'track_source' | 'input_collection';
  original_source_id: number;
}

class WorkflowService {
  private baseUrl = '/api/workflow';

  /**
   * Get all available platforms
   */
  async getAvailablePlatforms() {
    const response = await apiFetch(`${this.baseUrl}/input-collections/available_platforms/`);
    if (!response.ok) {
      throw new Error('Failed to fetch available platforms');
    }
    return response.json();
  }

  /**
   * Get available services for a platform
   */
  async getAvailableServices(platformId: number) {
    const response = await apiFetch(`${this.baseUrl}/input-collections/${platformId}/available_services/`);
    if (!response.ok) {
      throw new Error('Failed to fetch available services');
    }
    return response.json();
  }

  /**
   * Get all platform-service combinations
   */
  async getPlatformServices(): Promise<PlatformService[]> {
    const response = await apiFetch(`${this.baseUrl}/input-collections/platform_services/`);
    if (!response.ok) {
      throw new Error('Failed to fetch platform services');
    }
    return response.json();
  }

  /**
   * Get input collections for a project
   */
  async getInputCollections(projectId: number): Promise<InputCollection[]> {
    const response = await apiFetch(`${this.baseUrl}/input-collections/?project=${projectId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch input collections');
    }
    const data = await response.json();
    return data.results || data;
  }

  /**
   * Create a new input collection
   */
  async createInputCollection(data: CreateInputCollectionRequest): Promise<InputCollection> {
    const response = await apiFetch(`${this.baseUrl}/input-collections/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create input collection');
    }
    
    return response.json();
  }

  /**
   * Get workflow tasks for an input collection
   */
  async getWorkflowTasks(inputCollectionId: number): Promise<WorkflowTask[]> {
    const response = await apiFetch(`${this.baseUrl}/input-collections/${inputCollectionId}/workflow_tasks/`);
    if (!response.ok) {
      throw new Error('Failed to fetch workflow tasks');
    }
    return response.json();
  }

  /**
   * Retry a failed input collection
   */
  async retryInputCollection(inputCollectionId: number): Promise<{ message: string }> {
    const response = await apiFetch(`${this.baseUrl}/input-collections/${inputCollectionId}/retry/`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to retry input collection');
    }
    
    return response.json();
  }

  /**
   * Get workflow tasks by status
   */
  async getWorkflowTasksByStatus(status: string, projectId?: number): Promise<WorkflowTask[]> {
    let url = `${this.baseUrl}/workflow-tasks/by_status/?status=${status}`;
    if (projectId) {
      url += `&project=${projectId}`;
    }
    
    const response = await apiFetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch workflow tasks by status');
    }
    return response.json();
  }

  /**
   * Get all workflow tasks for a project
   */
  async getAllWorkflowTasks(projectId: number): Promise<WorkflowTask[]> {
    const response = await apiFetch(`${this.baseUrl}/workflow-tasks/?project=${projectId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch workflow tasks');
    }
    const data = await response.json();
    return data.results || data;
  }

  /**
   * Get all input collections including TrackSource data for a project
   */
  async getAllInputCollections(projectId: number): Promise<TrackSourceCollection[]> {
    try {
      console.log('=== getAllInputCollections DEBUG ===');
      console.log('Project ID:', projectId);
      
      // Fetch both InputCollection and TrackSource data
      const [inputCollectionsResponse, trackSourcesResponse] = await Promise.all([
        apiFetch(`${this.baseUrl}/input-collections/?project=${projectId}`),
        apiFetch(`/api/track-accounts/sources/?project=${projectId}&page_size=1000`)
      ]);

      console.log('InputCollections Response Status:', inputCollectionsResponse.status);
      console.log('TrackSources Response Status:', trackSourcesResponse.status);

      const collections: TrackSourceCollection[] = [];

      // Process InputCollection data
      if (inputCollectionsResponse.ok) {
        const inputData = await inputCollectionsResponse.json();
        const inputCollections = inputData.results || inputData;
        console.log('InputCollections found:', inputCollections.length);
        
        inputCollections.forEach((collection: InputCollection) => {
          collections.push({
            id: collection.id,
            name: `${collection.platform_name} - ${collection.service_name}`,
            platform_name: collection.platform_name,
            service_name: collection.service_name,
            urls: collection.urls,
            url_count: collection.url_count,
            status: collection.status,
            created_at: collection.created_at,
            updated_at: collection.updated_at,
            source_type: 'input_collection',
            original_source_id: collection.id
          });
        });
      } else {
        console.error('InputCollections API failed:', inputCollectionsResponse.status);
      }

      // Process TrackSource data
      if (trackSourcesResponse.ok) {
        const trackData = await trackSourcesResponse.json();
        const trackSources = trackData.results || trackData;
        console.log('TrackSources found:', trackSources.length);
        console.log('TrackSources data:', trackSources);
        
        trackSources.forEach((source: TrackSource) => {
          // Extract URLs from TrackSource
          const urls: string[] = [];
          if (source.facebook_link) urls.push(source.facebook_link);
          if (source.instagram_link) urls.push(source.instagram_link);
          if (source.linkedin_link) urls.push(source.linkedin_link);
          if (source.tiktok_link) urls.push(source.tiktok_link);
          if (source.other_social_media) urls.push(source.other_social_media);

          // Create separate collections for each platform that has URLs
          const platformUrls = {
            'Facebook': source.facebook_link ? [source.facebook_link] : [],
            'Instagram': source.instagram_link ? [source.instagram_link] : [],
            'LinkedIn': source.linkedin_link ? [source.linkedin_link] : [],
            'TikTok': source.tiktok_link ? [source.tiktok_link] : [],
            'Other': source.other_social_media ? [source.other_social_media] : []
          };

          Object.entries(platformUrls).forEach(([platform, platformUrls]) => {
            if (platformUrls.length > 0) {
              collections.push({
                id: source.id * 1000 + collections.length, // Generate unique ID
                name: `${source.name} - ${platform}`,
                platform_name: platform,
                service_name: 'Social Media',
                urls: platformUrls,
                url_count: platformUrls.length,
                status: 'pending', // TrackSource items start as pending
                created_at: source.created_at,
                updated_at: source.updated_at,
                source_type: 'track_source',
                original_source_id: source.id
              });
            }
          });
        });
      } else {
        console.error('TrackSources API failed:', trackSourcesResponse.status);
        const errorText = await trackSourcesResponse.text();
        console.error('TrackSources API error:', errorText);
      }

      console.log('Total collections created:', collections.length);
      console.log('Collections:', collections);
      console.log('=== END getAllInputCollections DEBUG ===');

      return collections;
    } catch (error) {
      console.error('Error fetching all input collections:', error);
      throw new Error('Failed to fetch input collections');
    }
  }
}

export const workflowService = new WorkflowService();
export default workflowService; 