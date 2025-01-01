import { FC, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLiveAudio } from '@/hooks/useLiveAudio';

interface LiveAudioRecorderProps {
  roomUrl: string;
  token: string;
  className?: string;
}

export const LiveAudioRecorder: FC<LiveAudioRecorderProps> = ({
  roomUrl,
  token,
  className
}) => {
  const {
    isConnected,
    isStreaming,
    currentTranscription,
    analysis,
    connect,
    disconnect,
    startStreaming,
    stopStreaming
  } = useLiveAudio(roomUrl, token);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  const handleToggleStreaming = async () => {
    if (isStreaming) {
      await stopStreaming();
    } else {
      await startStreaming();
    }
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Live Audio Recording</h3>
          <div className="flex items-center gap-2">
            <div className={cn(
              "w-2 h-2 rounded-full",
              isConnected ? "bg-green-500" : "bg-red-500"
            )} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="flex justify-center">
            <Button
              size="lg"
              variant={isStreaming ? "destructive" : "default"}
              onClick={handleToggleStreaming}
              disabled={!isConnected}
              className="h-16 w-16 rounded-full"
            >
              {isStreaming ? (
                <MicOff className="h-6 w-6" />
              ) : (
                <Mic className="h-6 w-6" />
              )}
            </Button>
          </div>

          {currentTranscription && (
            <div className="space-y-2">
              <h4 className="font-medium">Current Transcription:</h4>
              <p className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
                {currentTranscription}
              </p>
            </div>
          )}

          {analysis && (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-1">Sentiment:</h4>
                <div className={cn(
                  "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                  {
                    'bg-green-100 text-green-800': analysis.sentiment === 'positive',
                    'bg-yellow-100 text-yellow-800': analysis.sentiment === 'neutral',
                    'bg-red-100 text-red-800': analysis.sentiment === 'negative',
                  }
                )}>
                  {analysis.sentiment}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Keywords:</h4>
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-1">Summary:</h4>
                <p className="text-sm text-muted-foreground">
                  {analysis.summary}
                </p>
              </div>
            </div>
          )}

          {isStreaming && !currentTranscription && (
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Waiting for speech...
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}; 