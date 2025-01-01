import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TranscriptionEvaluation } from './components/TranscriptionEvaluation/TranscriptionEvaluation';
import { AudioUpload } from './components/AudioUpload/AudioUpload';
import { LiveAudioRecorder } from './components/LiveAudioRecorder/LiveAudioRecorder';
import { useTranscription } from './hooks/useTranscriptions';
import { useState } from 'react';
import { Card, CardContent, CardHeader } from './components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// In a real app, these would come from environment variables
const LIVEKIT_URL = 'wss://your-livekit-server.com';
const LIVEKIT_TOKEN = 'your-token-here';

function TranscriptionView({ id }: { id: string }) {
  const { data, isLoading, error } = useTranscription(id);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error loading transcription</div>;
  }

  if (!data) {
    return null;
  }

  return (
    <TranscriptionEvaluation
      details={data.details}
      evaluationResults={data.evaluationResults}
      onBack={() => console.log('Back clicked')}
    />
  );
}

function App() {
  const [currentTranscriptionId, setCurrentTranscriptionId] = useState<string | null>(null);
  const [audioAnalysis, setAudioAnalysis] = useState<any>(null);

  const handleUploadComplete = ({ audioUrl, analysis }: { audioUrl: string; analysis: any }) => {
    setAudioAnalysis(analysis);
    // The transcription ID will be set after the analysis is complete
    // and the transcription is created in the database
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="upload">Upload Audio</TabsTrigger>
              <TabsTrigger value="live">Live Recording</TabsTrigger>
            </TabsList>
            
            <TabsContent value="upload" className="space-y-8">
              <AudioUpload
                onUploadComplete={handleUploadComplete}
                className="mb-8"
              />

              {audioAnalysis && !currentTranscriptionId && (
                <Card>
                  <CardHeader>
                    <h2 className="text-xl font-semibold">Audio Analysis</h2>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h3 className="font-medium">Transcription:</h3>
                        <p className="text-sm text-muted-foreground">{audioAnalysis.transcription}</p>
                      </div>
                      <div>
                        <h3 className="font-medium">Sentiment:</h3>
                        <p className="text-sm text-muted-foreground capitalize">{audioAnalysis.sentiment}</p>
                      </div>
                      <div>
                        <h3 className="font-medium">Keywords:</h3>
                        <div className="flex flex-wrap gap-2">
                          {audioAnalysis.keywords.map((keyword: string, index: number) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-primary/10 rounded-full text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h3 className="font-medium">Summary:</h3>
                        <p className="text-sm text-muted-foreground">{audioAnalysis.summary}</p>
                      </div>
                      <div>
                        <h3 className="font-medium">Confidence Score:</h3>
                        <p className="text-sm text-muted-foreground">
                          {(audioAnalysis.confidenceScore * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="live">
              <LiveAudioRecorder
                roomUrl={LIVEKIT_URL}
                token={LIVEKIT_TOKEN}
              />
            </TabsContent>
          </Tabs>

          {currentTranscriptionId && (
            <TranscriptionView id={currentTranscriptionId} />
          )}
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;