// Agent types
export interface Agent {
  id: string;
  name: string;
  description: string;
  personality: string;
  tools: string[];
  memory_type: string;
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  agent_id?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  agent_id: string;
  conversation_id: string;
  memory_used: boolean;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface AgentsResponse {
  agents: Agent[];
}

export interface ConversationHistory {
  conversation_id: string;
  messages: ChatMessage[];
} 