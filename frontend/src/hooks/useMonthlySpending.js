import { useState, useMemo } from "react";
import { useGetMonthlyTrend } from "../features/budget/useGetMonthlyTrend";
import { useBudgetSuggestions } from "../features/budget/useBudgetSuggestions";
import { getLocalISODate } from "../utils/constants";

export const useMonthlySpending = (initialCategory = "All") => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);

  const getMonthRange = (date) => {
    if (!date) return { start: null };

    let dateObj;

    if (typeof date === "string") {
      dateObj = new Date(date + "-01T00:00:00");
    } else {
      dateObj = date;
    }

    const firstDay = new Date(dateObj.getFullYear(), dateObj.getMonth(), 1);

    return {
      start: getLocalISODate(firstDay, "daily"),
    };
  };
  const { start } = getMonthRange(selectedDate);

  const { data: suggestionData } = useBudgetSuggestions(3);

  const {
    data: trendData,
    isLoading,
    isFetching,
  } = useGetMonthlyTrend(
    {
      start_date: start,
      category: selectedCategory === "All" ? "" : selectedCategory,
    },
    {
      enabled: Boolean(selectedDate) && Boolean(suggestionData),
    },
  );

  const chartData = useMemo(() => {
    const rawTrend = trendData?.data?.data || [];
    const suggestions = suggestionData?.suggestions || [];

    return rawTrend.map((m) => {
      let allocatedAmount = 0;

      if (selectedCategory === "All") {
        allocatedAmount = suggestionData?.totalBudget || 0;
      } else {
        const catSuggestion = suggestions.find(
          (s) => s.category_name === selectedCategory,
        );
        allocatedAmount = catSuggestion
          ? parseFloat(catSuggestion.suggested_amount)
          : 0;
      }

      return {
        month: m.month_label,
        spent: parseFloat(m.total),
        allocated: allocatedAmount,
      };
    });
  }, [trendData, suggestionData, selectedCategory]);

  return {
    selectedDate,
    setSelectedDate,
    selectedCategory,
    setSelectedCategory,
    chartData: chartData || [],
    isLoading,
    isFetching,
  };
};
