import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api';

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: analyticsApi.getOverview,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
} 