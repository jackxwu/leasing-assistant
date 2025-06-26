import { ChatRequest, ChatResponse } from '../types/chat';
import { getOrCreateClientId } from '../utils/clientId';

const API_BASE_URL = 'http://localhost:8000';

export interface ConversationHistory {
  client_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

export const chatApi = {
  async sendMessage(request: Omit<ChatRequest, 'client_id'>): Promise<ChatResponse> {
    // Add client_id to the request
    const requestWithClientId: ChatRequest = {
      ...request,
      client_id: getOrCreateClientId()
    };

    const response = await fetch(`${API_BASE_URL}/api/reply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestWithClientId),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  },

  async getConversationHistory(): Promise<ConversationHistory> {
    const clientId = getOrCreateClientId();
    const response = await fetch(`${API_BASE_URL}/api/conversation/${clientId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  },
};