import { useState, useEffect } from 'react';
import { Actor } from '@/lib/actors/Actor';

interface ActorState {
  state: any;
  error: Error | null;
}

export function useActor(actor: Actor): ActorState {
  const [state, setState] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const subscription = actor.receive().subscribe({
      next: (value) => {
        setState(value);
        setError(null);
      },
      error: (err) => {
        setError(err);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [actor]);

  return { state, error };
} 