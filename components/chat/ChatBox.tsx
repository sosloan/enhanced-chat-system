import React, { useState } from 'react';
import { Chat, Message } from '@/types/chat';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { MessageBubble } from './MessageBubble';

interface ChatBoxProps {
  chat: Chat;
  onSendMessage: (content: string) => void;
  onToggleWebhook: () => void;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
  chat,
  onSendMessage,
  onToggleWebhook
}) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const renderMessageMetrics = (message: Message) => {
    if (!message.sentiment && !message.priority && !message.category) {
      return null;
    }

    return (
      <div className="flex gap-2 mt-1">
        {message.sentiment !== undefined && (
          <Badge variant={message.sentiment > 0.5 ? "success" : "destructive"}>
            Sentiment: {(message.sentiment * 100).toFixed(0)}%
          </Badge>
        )}
        {message.priority !== undefined && (
          <Badge variant="secondary">
            Priority: {(message.priority * 100).toFixed(0)}%
          </Badge>
        )}
        {message.category && (
          <Badge variant="outline">
            {message.category}
          </Badge>
        )}
      </div>
    );
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex flex-col">
          <h3 className="font-semibold">{chat.title}</h3>
          <p className="text-sm text-muted-foreground">
            {chat.participants.length} participants
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Webhook</span>
          <Button
            variant={chat.isWebhookEnabled ? "default" : "secondary"}
            size="sm"
            onClick={onToggleWebhook}
          >
            {chat.isWebhookEnabled ? "Enabled" : "Disabled"}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-grow overflow-y-auto p-4 space-y-4">
        {chat.messages.map((message, index) => (
          <div key={message.id} className="space-y-1">
            <MessageBubble message={message} />
            {renderMessageMetrics(message)}
          </div>
        ))}
      </CardContent>

      <CardFooter className="p-4 pt-2">
        <form onSubmit={handleSubmit} className="flex w-full space-x-2">
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-grow"
          />
          <Button type="submit">Send</Button>
        </form>
      </CardFooter>
    </Card>
  );
}; 