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
  type: MessageType;
  text: string;
  user: User;
  timestamp: number;
  sentiment?: number;
  priority?: number;
  category?: string;
  metadata?: Record<string, any>;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  isWebhookEnabled: boolean;
  participants: User[];
  metadata?: Record<string, any>;
}

export interface ChatState {
  chats: Chat[];
  activeChat?: string;
  loading: boolean;
  error?: string;
} 