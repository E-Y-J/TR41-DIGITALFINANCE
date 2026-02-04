import { useState, useEffect } from "react";

const generateMonthlyData = (startDate, category) => {
  if (category === "Government & Legal") return [];

  const data = [];
  const now = new Date();

  let current = new Date(startDate.getFullYear(), startDate.getMonth(), 1);

  while (current <= now) {
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, "0");
    const rawMonthValue = `${year}-${month}`;

    const spent = Math.floor(Math.random() * 2000) + 500;
    const allocated = 2500;

    data.push({
      month: rawMonthValue,
      spent: spent,
      allocated: allocated,
    });

    current.setMonth(current.getMonth() + 1);
  }
  return data;
};

export const useMonthlySpending = (initialDate, initialCategory) => {
  const [selectedDate, setSelectedDate] = useState(initialDate || new Date());
  const [selectedCategory, setSelectedCategory] = useState(
    initialCategory || "All",
  );
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleDateChange = (newDate) => {
    setIsLoading(true);
    setSelectedDate(newDate);
  };

  useEffect(() => {
    // Replace with your API call: GET /api/spending/monthly?start=${selectedDate}
    const timer = setTimeout(() => {
      const data = generateMonthlyData(selectedDate, selectedCategory);
      setChartData(data);
      setIsLoading(false);
    }, 600);
    return () => clearTimeout(timer);
  }, [selectedDate, selectedCategory]);

  return {
    selectedDate,
    setSelectedDate: handleDateChange,
    selectedCategory,
    setSelectedCategory,
    chartData,
    isLoading,
  };
};
