import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import feathers from '@feathersjs/client';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { MessageActor } from '@/lib/actors/MessageActor';
import { Chat, Message, MessageType, User } from '@/types/chat';
import { useActor } from '@/hooks/useActor';
import { ChatBox } from '@/components/chat/ChatBox';

// Setup Feathers client
const socket = io('http://localhost:3030');
const client = feathers();
client.configure(feathers.socketio(socket));
client.configure(feathers.authentication());

// Initialize message actor
const messageActor = new MessageActor();

const ChatUIGrid: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [chats, setChats] = useState<Chat[]>([
    { id: '1', title: 'Chat 1 (Left Column)', messages: [], isWebhookEnabled: false, participants: [] },
    { id: '2', title: 'Chat 2 (Top Right)', messages: [], isWebhookEnabled: false, participants: [] },
    { id: '3', title: 'Chat 3 (Bottom Right)', messages: [], isWebhookEnabled: false, participants: [] },
  ]);

  // Subscribe to message actor updates
  const { state: messageState, error: messageError } = useActor(messageActor);

  useEffect(() => {
    // Authenticate and get user
    const setupClient = async () => {
      try {
        const response = await client.authenticate();
        setUser(response.user);
        
        const messages = await client.service('messages').find({
          query: {
            $sort: { createdAt: -1 },
            $limit: 25
          }
        });

        // Process messages through ML pipeline
        const processedMessages = await Promise.all(
          messages.data.reverse().map(msg => messageActor.processMessage(msg))
        );

        // Add messages to all chats
        setChats(prevChats => prevChats.map(chat => ({
          ...chat,
          messages: processedMessages,
          participants: [...chat.participants, response.user]
        })));
      } catch (error) {
        console.error('Error authenticating or fetching messages:', error);
      }
    };

    setupClient();

    // Listen for new messages
    client.service('messages').on('created', async (message: Message) => {
      // Process message through ML pipeline
      const processedMessage = await messageActor.processMessage(message);
      
      setChats(prevChats => prevChats.map(chat => ({
        ...chat,
        messages: [...chat.messages, processedMessage]
      })));

      // Analyze message patterns periodically
      const patterns = await messageActor.analyzeMessagePatterns();
      console.log('Message patterns:', patterns);
    });

    return () => {
      client.service('messages').removeAllListeners('created');
    };
  }, []);

  const sendMessage = async (chatId: string, text: string) => {
    if (!user) {
      console.error('User not authenticated');
      return;
    }

    try {
      const message: Partial<Message> = {
        type: MessageType.TEXT,
        text,
        user,
        timestamp: Date.now()
      };

      const createdMessage = await client.service('messages').create(message);
      
      // Process message through ML pipeline
      const processedMessage = await messageActor.processMessage(createdMessage);

      // Simulate webhook functionality with ML-enhanced messages
      chats.forEach(chat => {
        if (chat.id !== chatId && chat.isWebhookEnabled) {
          setTimeout(async () => {
            const webhookMessage: Message = {
              ...processedMessage,
              id: Math.random().toString(),
              user: { ...user, email: `Webhook from Chat ${chatId}` },
              metadata: {
                source: 'webhook',
                originalChatId: chatId
              }
            };

            setChats(prevChats => 
              prevChats.map(c => 
                c.id === chat.id
                  ? { ...c, messages: [...c.messages, webhookMessage] }
                  : c
              )
            );

            // Improve model based on webhook interaction
            await messageActor.improveResponses({
              originalMessage: processedMessage,
              webhookMessage,
              interaction: 'webhook_forward'
            });
          }, 1000);
        }
      });
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const toggleWebhook = (chatId: string) => {
    setChats(prevChats => 
      prevChats.map(chat => 
        chat.id === chatId ? { ...chat, isWebhookEnabled: !chat.isWebhookEnabled } : chat
      )
    );
  };

  if (!user) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <div className="grid grid-cols-2 gap-4 p-4 h-screen bg-gray-100">
      <Alert className="col-span-2">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Enhanced Chat System</AlertTitle>
        <AlertDescription>
          This demo uses Feathers Chat with ML-powered message processing and actor-based architecture.
          Messages are analyzed for sentiment, priority, and patterns in real-time.
        </AlertDescription>
      </Alert>
      
      <div className="row-span-2">
        <ChatBox
          chat={chats[0]}
          onSendMessage={(content) => sendMessage(chats[0].id, content)}
          onToggleWebhook={() => toggleWebhook(chats[0].id)}
        />
      </div>
      
      <div>
        <ChatBox
          chat={chats[1]}
          onSendMessage={(content) => sendMessage(chats[1].id, content)}
          onToggleWebhook={() => toggleWebhook(chats[1].id)}
        />
      </div>
      
      <div>
        <ChatBox
          chat={chats[2]}
          onSendMessage={(content) => sendMessage(chats[2].id, content)}
          onToggleWebhook={() => toggleWebhook(chats[2].id)}
        />
      </div>
    </div>
  );
};

export default ChatUIGrid; 