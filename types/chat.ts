export enum MessageType {
  TEXT = 'text',
  SYSTEM = 'system',
  ERROR = 'error'
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: Date;
  sentiment?: number;
  priority?: number;
  category?: string;
}

export interface Chat {
  id: string;
  title: string;
  participants: string[];
  messages: Message[];
  isWebhookEnabled: boolean;
}

export interface ChatMetrics {
  sentiment: number;
  priority: number;
  category: string;
}

export interface ChatState {
  chats: Chat[];
  activeChat?: string;
  loading: boolean;
  error?: string;
} 