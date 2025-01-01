import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { evaluationApi, EvaluationResultCreate } from '@/lib/api';

export function useEvaluations(transcriptionId: string) {
  return useQuery({
    queryKey: ['evaluations', transcriptionId],
    queryFn: () => evaluationApi.list(transcriptionId),
    enabled: !!transcriptionId,
  });
}

export function useEvaluation(id: string) {
  return useQuery({
    queryKey: ['evaluation', id],
    queryFn: () => evaluationApi.get(id),
    enabled: !!id,
  });
}

export function useCreateEvaluation(transcriptionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EvaluationResultCreate) =>
      evaluationApi.create(transcriptionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluations', transcriptionId] });
      queryClient.invalidateQueries({ queryKey: ['transcription', transcriptionId] });
    },
  });
}

export function useUpdateEvaluation(evaluationId: string, transcriptionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EvaluationResultCreate) =>
      evaluationApi.update(evaluationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluation', evaluationId] });
      queryClient.invalidateQueries({ queryKey: ['evaluations', transcriptionId] });
      queryClient.invalidateQueries({ queryKey: ['transcription', transcriptionId] });
    },
  });
}

export function useDeleteEvaluation(transcriptionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => evaluationApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluations', transcriptionId] });
      queryClient.invalidateQueries({ queryKey: ['transcription', transcriptionId] });
    },
  });
} 