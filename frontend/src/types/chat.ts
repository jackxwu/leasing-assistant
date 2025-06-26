export interface Lead {
  name: string;
  email: string;
}

export interface Preferences {
  bedrooms?: number;
  move_in?: string;
}

export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

export interface ChatRequest {
  lead: Lead;
  message: string;
  preferences?: Preferences;
  community_id: string;
  client_id: string;
}

export interface ChatResponse {
  reply: string;
  action: 'propose_tour' | 'ask_clarification' | 'handoff_human';
  proposed_time?: string;
}