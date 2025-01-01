import React from 'react';
import { Message } from '@/types/chat';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm font-medium">{message.sender}</span>
        <span className="text-xs text-muted-foreground">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
      <div
        className={cn(
          "rounded-lg p-3 max-w-[80%]",
          "bg-primary text-primary-foreground"
        )}
      >
        {message.content}
      </div>
    </div>
  );
}; 