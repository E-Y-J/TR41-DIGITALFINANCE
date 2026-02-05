import { useState } from "react";
import { useGetMonthlyTrend } from "../features/budget/useGetMonthlyTrend";
import { getLocalISODate } from "../utils/constants";

export const useMonthlySpending = (initialCategory = "All") => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);

  const getMonthRange = (date) => {
    if (!date) return { start: null };

    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);

    return {
      start: getLocalISODate(firstDay, "daily"),
    };
  };

  const { start } = getMonthRange(selectedDate);

  const {
    data: chartData,
    isLoading,
    isFetching,
  } = useGetMonthlyTrend(
    {
      start_date: start,
      category: selectedCategory === "All" ? "" : selectedCategory,
    },
    {
      enabled: Boolean(selectedDate),
      select: (response) => {
        const trendArray = response?.data?.data || [];
        return trendArray.map((m) => ({
          month: m.month_label,
          spent: parseFloat(m.total),
          allocated: 1500,
        }));
      },
    },
  );

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
