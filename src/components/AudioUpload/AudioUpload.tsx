import { FC, useCallback, useState, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, X, PlayCircle, PauseCircle, SkipBack, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAudioProcessor } from '@/hooks/useAudioProcessor';
import { TranscriptionResult } from '@/lib/openai';

interface AudioUploadProps {
  onUploadComplete: (result: { audioUrl: string; analysis: any }) => void;
  className?: string;
}

export const AudioUpload: FC<AudioUploadProps> = ({ onUploadComplete, className }) => {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [segments, setSegments] = useState<TranscriptionResult['segments']>([]);
  const [currentSegment, setCurrentSegment] = useState<number>(-1);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { processAudio, isProcessing, progress } = useAudioProcessor();

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.addEventListener('timeupdate', handleTimeUpdate);
      audioRef.current.addEventListener('loadedmetadata', handleLoadedMetadata);
      audioRef.current.addEventListener('ended', () => setIsPlaying(false));
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.removeEventListener('timeupdate', handleTimeUpdate);
        audioRef.current.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audioRef.current.removeEventListener('ended', () => setIsPlaying(false));
      }
    };
  }, []);

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setCurrentTime(audioRef.current.currentTime);
    
    // Update current segment
    const newSegmentIndex = segments.findIndex(
      segment => 
        audioRef.current!.currentTime >= segment.start && 
        audioRef.current!.currentTime <= segment.end
    );
    
    if (newSegmentIndex !== currentSegment) {
      setCurrentSegment(newSegmentIndex);
    }
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration);
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Create local URL for preview
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    if (audioRef.current) {
      audioRef.current.src = url;
    }

    // Process the audio file
    try {
      const result = await processAudio(file);
      setSegments(result.segments || []);
      onUploadComplete({ audioUrl: url, analysis: result });
    } catch (error) {
      console.error('Error processing audio:', error);
      // Handle error appropriately
    }
  }, [onUploadComplete, processAudio]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a']
    },
    maxFiles: 1,
  });

  const togglePlay = useCallback(() => {
    if (!audioRef.current || !audioUrl) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }, [audioUrl, isPlaying]);

  const seekToSegment = useCallback((direction: 'next' | 'prev') => {
    if (!audioRef.current || segments.length === 0) return;

    let newSegmentIndex = currentSegment;
    if (direction === 'next') {
      newSegmentIndex = Math.min(segments.length - 1, currentSegment + 1);
    } else {
      newSegmentIndex = Math.max(0, currentSegment - 1);
    }

    if (newSegmentIndex !== currentSegment && segments[newSegmentIndex]) {
      audioRef.current.currentTime = segments[newSegmentIndex].start;
      setCurrentSegment(newSegmentIndex);
    }
  }, [currentSegment, segments]);

  const clearAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    setIsPlaying(false);
    setSegments([]);
    setCurrentSegment(-1);
    setCurrentTime(0);
    setDuration(0);
  }, [audioUrl]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <h3 className="text-lg font-semibold">Upload Audio</h3>
      </CardHeader>
      <CardContent>
        {!audioUrl ? (
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25"
            )}
          >
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 mx-auto mb-4 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {isDragActive
                ? "Drop the audio file here"
                : "Drag & drop an audio file here, or click to select"}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => seekToSegment('prev')}
                  disabled={currentSegment <= 0}
                >
                  <SkipBack className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={togglePlay}
                >
                  {isPlaying ? (
                    <PauseCircle className="w-4 h-4" />
                  ) : (
                    <PlayCircle className="w-4 h-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => seekToSegment('next')}
                  disabled={currentSegment >= segments.length - 1}
                >
                  <SkipForward className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex-1 text-sm">
                <div className="truncate">
                  {audioUrl.split('/').pop()}
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={clearAudio}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            <div className="relative h-8 bg-muted rounded-lg overflow-hidden">
              {segments.map((segment, index) => {
                const startPercent = (segment.start / duration) * 100;
                const widthPercent = ((segment.end - segment.start) / duration) * 100;
                return (
                  <div
                    key={index}
                    className={cn(
                      "absolute h-full transition-colors",
                      index === currentSegment
                        ? "bg-primary"
                        : "bg-primary/30 hover:bg-primary/50"
                    )}
                    style={{
                      left: `${startPercent}%`,
                      width: `${widthPercent}%`
                    }}
                    title={segment.text}
                    onClick={() => {
                      if (audioRef.current) {
                        audioRef.current.currentTime = segment.start;
                        setCurrentSegment(index);
                      }
                    }}
                  />
                );
              })}
              <div
                className="absolute h-full bg-primary/50 w-0.5"
                style={{
                  left: `${(currentTime / duration) * 100}%`
                }}
              />
            </div>

            {currentSegment !== -1 && segments[currentSegment] && (
              <div className="text-sm text-center p-2 bg-muted rounded">
                {segments[currentSegment].text}
              </div>
            )}

            {isProcessing && (
              <div className="space-y-2">
                <Progress value={progress} className="w-full" />
                <p className="text-sm text-muted-foreground text-center">
                  Processing audio... {Math.round(progress)}%
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 