import { useState } from "react";
import { useGetTransactionBreakdown } from "../features/budget/useGetTransactionBreakdown";
import { CATEGORIES, getLocalISODate } from "../utils/constants";

export const useDailyBreakdown = (
  initialDate = null,
  initialEndDate = null,
  initialCategory = "All",
) => {
  const [specificDate, setSpecificDate] = useState(initialDate);
  const [endDate, setEndDate] = useState(initialEndDate);
  const [specificCategory, setSpecificCategory] = useState(initialCategory);

  const {
    data: dailyCategoryData,
    isLoading,
    isFetching,
  } = useGetTransactionBreakdown(
    {
      start_date: getLocalISODate(specificDate),
      end_date: getLocalISODate(endDate || specificDate),
    },
    {
      enabled: Boolean(specificDate),

      select: (response) => {
        const summaryData = response?.data?.data || response?.data || {};
        const categoryTotals = summaryData.categories || [];

        if (!specificDate) return [];

        const dateObj =
          typeof specificDate === "string"
            ? new Date(specificDate + "T00:00:00")
            : specificDate;

        const dayLabel = dateObj.toLocaleDateString("en-US", {
          month: "short",
          day: endDate ? undefined : "numeric",
          year: endDate ? "numeric" : undefined,
        });

        const dataEntry = { day: dayLabel };
        CATEGORIES.forEach((cat) => {
          dataEntry[cat] = 0;
        });

        categoryTotals.forEach((item) => {
          const catName = item.category;
          const totalAmount = parseFloat(item.total || 0);

          if (dataEntry[catName] !== undefined) {
            dataEntry[catName] = totalAmount;
          }
        });

        return [dataEntry];
      },
    },
  );

  const handleDateChange = (newDate) => {
    setSpecificDate(newDate);
  };

  return {
    specificDate,
    setSpecificDate: handleDateChange,
    endDate,
    setEndDate,
    specificCategory,
    setSpecificCategory,
    dailyCategoryData: dailyCategoryData || [],
    isLoading,
    isFetching,
    hasSelectedDate: !!specificDate,
  };
};
