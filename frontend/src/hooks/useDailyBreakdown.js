import { useState } from "react";
import { useGetDailyBreakdown } from "../features/budget/useGetDailyBreakdown";
import { CATEGORIES, getLocalISODate } from "../utils/constants";

export const useDailyBreakdown = () => {
  const [specificDate, setSpecificDate] = useState(null);
  const [specificCategory, setSpecificCategory] = useState("All");

  const {
    data: dailyCategoryData,
    isLoading,
    isFetching,
  } = useGetDailyBreakdown(
    {
      start_date: getLocalISODate(specificDate),
      end_date: getLocalISODate(specificDate),
    },
    {
      enabled: Boolean(specificDate),

      select: (response) => {
        const summaryData = response?.data?.data || {};
        const categoryTotals = summaryData.categories || [];

        if (!specificDate) return [];

        const dayLabel = specificDate.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });

        const dataEntry = { day: dayLabel };
        CATEGORIES.forEach((cat) => (dataEntry[cat] = 0));

        categoryTotals.forEach((item) => {
          const catName = item.category;
          const totalAmount = parseFloat(item.total);

          if (dataEntry[catName] !== undefined) {
            dataEntry[catName] = totalAmount;
          }
        });

        console.log("Fixed Daily Breakdown:", dataEntry);
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
    specificCategory,
    setSpecificCategory,
    dailyCategoryData,
    isLoading,
    isFetching,
    hasSelectedDate: !!specificDate,
  };
};
