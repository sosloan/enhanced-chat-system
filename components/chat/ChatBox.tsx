// This file is part of MinIO Design System
// Copyright (c) 2024 MinIO, Inc.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

import React, { useState } from 'react';
import { Chat, Message } from '@/types/chat';
import { useAudit } from '@/hooks/useAudit';

interface ChatBoxProps {
  chat: Chat;
  onSendMessage: (content: string) => Promise<void>;
  onToggleWebhook: () => void;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
  chat,
  onSendMessage,
  onToggleWebhook
}) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { logChatEvent, logError } = useAudit();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setIsLoading(true);
      setError(null);
      const startTime = Date.now();
      
      try {
        await logChatEvent(
          'POST',
          '/api/chat/message',
          chat.id,
          undefined,
          {
            chatId: chat.id,
            messageContent: input,
          }
        );
        
        await onSendMessage(input);
        setInput('');
        
        // Log successful message send
        await logChatEvent(
          'POST',
          '/api/chat/message',
          chat.id,
          undefined,
          {
            chatId: chat.id,
            status: 'success',
            duration: Date.now() - startTime,
          }
        );
      } catch (error) {
        console.error('Failed to send message:', error);
        setError('Failed to send message. Please try again.');
        
        // Log error
        if (error instanceof Error) {
          await logError(
            error,
            'POST',
            '/api/chat/message',
            chat.id,
            {
              chatId: chat.id,
              messageContent: input,
            }
          );
        }
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleToggleWebhook = async () => {
    try {
      await logChatEvent(
        'PUT',
        '/api/chat/webhook',
        chat.id,
        undefined,
        {
          chatId: chat.id,
          webhookEnabled: !chat.isWebhookEnabled,
        }
      );
      
      onToggleWebhook();
    } catch (error) {
      if (error instanceof Error) {
        await logError(
          error,
          'PUT',
          '/api/chat/webhook',
          chat.id,
          {
            chatId: chat.id,
            webhookEnabled: !chat.isWebhookEnabled,
          }
        );
      }
    }
  };

  const renderMessageMetrics = (message: Message) => {
    if (!message.sentiment && !message.priority && !message.category) {
      return null;
    }

    return (
      <div className="flex gap-2 mt-1">
        {message.sentiment !== undefined && (
          <div className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
            message.sentiment > 0.5 
              ? "border-transparent bg-success text-success-foreground"
              : "border-transparent bg-destructive text-destructive-foreground"
          }`}>
            Sentiment: {(message.sentiment * 100).toFixed(0)}%
          </div>
        )}
        {message.priority !== undefined && (
          <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold border-transparent bg-secondary text-secondary-foreground">
            Priority: {(message.priority * 100).toFixed(0)}%
          </div>
        )}
        {message.category && (
          <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-foreground">
            {message.category}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full rounded-lg border bg-card text-card-foreground shadow-sm">
      <div className="flex flex-row items-center justify-between space-y-0 pb-2 p-6">
        <div className="flex flex-col">
          <h3 className="font-semibold">{chat.title}</h3>
          <p className="text-sm text-muted-foreground">
            {chat.participants.length} participants
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Webhook</span>
          <button
            className={`inline-flex items-center justify-center rounded-md text-sm font-medium h-9 px-3
              ${chat.isWebhookEnabled 
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
              }`}
            onClick={handleToggleWebhook}
            aria-pressed={chat.isWebhookEnabled}
          >
            {chat.isWebhookEnabled ? "Enabled" : "Disabled"}
          </button>
        </div>
      </div>

      <div 
        className="flex-grow overflow-y-auto p-4 space-y-4"
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
      >
        {chat.messages.map((message) => (
          <div key={message.id} className="space-y-1">
            <div className="flex flex-col">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium">{message.sender}</span>
                <span className="text-xs text-muted-foreground">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="rounded-lg p-3 max-w-[80%] bg-primary text-primary-foreground">
                {message.content}
              </div>
            </div>
            {renderMessageMetrics(message)}
          </div>
        ))}
      </div>

      <div className="p-4 pt-2">
        <form onSubmit={handleSubmit} className="flex w-full space-x-2">
          {error && (
            <div className="text-sm text-destructive mb-2" role="alert">
              {error}
            </div>
          )}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm
              ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium
              placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2
              focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Message input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            aria-busy={isLoading}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium h-10 px-4
              bg-primary text-primary-foreground hover:bg-primary/90
              disabled:opacity-50 disabled:pointer-events-none"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}; 