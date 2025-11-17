import { useQuery } from "@tanstack/react-query";
import { getDailyPostRequest } from "./getDailyPosts";

export function useDailyPostQuery() {
  return useQuery({
    queryKey: ["daily-post"],
    queryFn: getDailyPostRequest,
    staleTime: 1000 * 60,     // 1 minute
    refetchOnWindowFocus: false,
  });
}
