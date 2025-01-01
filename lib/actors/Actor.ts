import { Subject, Observable } from 'rxjs';

export abstract class Actor {
  protected readonly id: string;
  protected mailbox: Subject<any>;
  
  constructor(id: string) {
    this.id = id;
    this.mailbox = new Subject();
  }

  protected send(message: any): void {
    this.mailbox.next(message);
  }

  public receive(): Observable<any> {
    return this.mailbox.asObservable();
  }

  public getId(): string {
    return this.id;
  }
} 