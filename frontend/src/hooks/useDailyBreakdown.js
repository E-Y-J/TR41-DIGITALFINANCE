import { useState, useEffect } from "react";
import { CATEGORIES } from "../utils/constants";

const generateDailyCategoryData = (date) => {
  if (!date) return [];
  const dayLabel = date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
  const dataEntry = { day: dayLabel };

  CATEGORIES.forEach((cat) => {
    dataEntry[cat] = Math.floor(Math.random() * 100) + 10;
  });

  return [dataEntry];
};

export const useDailyBreakdown = () => {
  const [specificDate, setSpecificDate] = useState(null);
  const [specificCategory, setSpecificCategory] = useState("All"); // Added this
  const [dailyCategoryData, setDailyCategoryData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleDateChange = (newDate) => {
    setIsLoading(true);
    setSpecificDate(newDate);
  };

  useEffect(() => {
    if (!specificDate) return;

    const timer = setTimeout(() => {
      const dailyData = generateDailyCategoryData(specificDate);
      setDailyCategoryData(dailyData);
      setIsLoading(false);
    }, 600);
    return () => clearTimeout(timer);
  }, [specificDate]);

  return {
    specificDate,
    setSpecificDate: handleDateChange,
    specificCategory,
    setSpecificCategory,
    dailyCategoryData,
    isLoading,
    hasSelectedDate: !!specificDate,
  };
};
