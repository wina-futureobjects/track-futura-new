import { apiFetch } from '../utils/api';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  is_error?: boolean;
}

export interface ChatThread {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  messages: Message[];
  last_message: Message | null;
}

class ChatService {
  async createThread(): Promise<ChatThread> {
    const response = await apiFetch('/api/chat/threads/', {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to create chat thread');
    return response.json();
  }

  async getThreads(): Promise<ChatThread[]> {
    const response = await apiFetch('/api/chat/threads/');
    if (!response.ok) throw new Error('Failed to fetch chat threads');
    return response.json();
  }

  async getThread(threadId: string): Promise<ChatThread> {
    const response = await apiFetch(`/api/chat/threads/${threadId}/`);
    if (!response.ok) throw new Error('Failed to fetch chat thread');
    return response.json();
  }

  async addMessage(threadId: string, content: string, sender: 'user' | 'ai', projectId?: string): Promise<Message> {
    const body: any = {
      content,
      sender,
    };

    // Add project_id if available for AI analysis
    if (projectId) {
      body.project_id = projectId;
    }

    const response = await apiFetch(`/api/chat/threads/${threadId}/add_message/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error('Failed to add message');
    return response.json();
  }

  async archiveThread(threadId: string): Promise<void> {
    const response = await apiFetch(`/api/chat/threads/${threadId}/archive/`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to archive thread');
  }
}

export const chatService = new ChatService(); 