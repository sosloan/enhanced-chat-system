import React from 'react';
import { Message, MessageType } from '@/types/chat';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isSystem = message.type === MessageType.SYSTEM;
  const isError = message.type === MessageType.ERROR;

  const getInitials = (email: string) => {
    return email
      .split('@')[0]
      .split('.')
      .map(part => part[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="flex items-start space-x-2">
      <Avatar className="h-8 w-8">
        <AvatarImage src={`https://avatar.vercel.sh/${message.user.email}`} />
        <AvatarFallback>{getInitials(message.user.email)}</AvatarFallback>
      </Avatar>
      
      <div className="flex flex-col space-y-1 flex-1">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium">
            {message.user.name || message.user.email}
          </span>
          <span className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        
        <div
          className={cn(
            "rounded-lg px-3 py-2 text-sm",
            isSystem && "bg-muted text-muted-foreground",
            isError && "bg-destructive text-destructive-foreground",
            !isSystem && !isError && "bg-primary text-primary-foreground"
          )}
        >
          {message.text}
        </div>

        {message.metadata && (
          <div className="text-xs text-muted-foreground mt-1">
            {Object.entries(message.metadata).map(([key, value]) => (
              <span key={key} className="mr-2">
                {key}: {value}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}; 