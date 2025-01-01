import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transcriptionApi, TranscriptionCreate } from '@/lib/api';

export function useTranscriptions(page = 0, limit = 10) {
  return useQuery({
    queryKey: ['transcriptions', page, limit],
    queryFn: () => transcriptionApi.list(page * limit, limit),
  });
}

export function useTranscription(id: string) {
  return useQuery({
    queryKey: ['transcription', id],
    queryFn: () => transcriptionApi.get(id),
    enabled: !!id,
  });
}

export function useTranscriptionCreate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TranscriptionCreate) => transcriptionApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcriptions'] });
    },
  });
}

export function useTranscriptionDelete() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => transcriptionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcriptions'] });
    },
  });
} 