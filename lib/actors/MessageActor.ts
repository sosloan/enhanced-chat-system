import { Actor } from '@/lib/actors/Actor';
import { Message, MessageType } from '@/types/chat';
import { MLProcessor } from '@/lib/ml/MLProcessor';
import { BehaviorSubject, Observable } from 'rxjs';

export class MessageActor extends Actor {
  private messages: BehaviorSubject<Message[]>;
  private mlProcessor: MLProcessor;

  constructor() {
    super('MessageActor');
    this.messages = new BehaviorSubject<Message[]>([]);
    this.mlProcessor = new MLProcessor();
  }

  public async processMessage(message: Message): Promise<Message> {
    // Process message through ML pipeline
    const enrichedMessage = await this.mlProcessor.processMessage(message);
    
    // Update message store
    const currentMessages = this.messages.value;
    this.messages.next([...currentMessages, enrichedMessage]);
    
    return enrichedMessage;
  }

  public getMessages(): Observable<Message[]> {
    return this.messages.asObservable();
  }

  public async analyzeMessagePatterns(): Promise<any> {
    return this.mlProcessor.analyzePatterns(this.messages.value);
  }

  public async improveResponses(feedback: any): Promise<void> {
    await this.mlProcessor.improveModel(feedback);
  }
} 