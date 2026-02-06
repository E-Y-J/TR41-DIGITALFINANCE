import { getSuggestions } from "../../api/transactions";
import { useQuery } from "@tanstack/react-query";
import { useAxios } from "../../hooks/useAxios";

export const useBudgetSuggestions = (months = 3) => {
  const apiClient = useAxios();

  return useQuery({
    queryKey: ["budget-suggestions", months],
    queryFn: () => getSuggestions(apiClient, { months }),
    staleTime: 1000 * 60 * 5,

    select: (response) => {
      const payload = response?.data?.data || {};

      return {
        suggestions: payload.suggestions || [],
        totalBudget: payload.total_suggested_budget || 0,
        analysis: payload.analysis_period || {},
        summary: payload.recommendation_summary || {},
      };
    },
  });
};
