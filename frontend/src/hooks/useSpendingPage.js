import { useState, useEffect, useMemo } from "react";
import { useGetUser } from "../features/auth/useGetUser";
import { formatDate } from "../utils/constants";

const generateDailyData = (date, category) => {
  const daysInMonth = new Date(
    date.getFullYear(),
    date.getMonth() + 1,
    0,
  ).getDate();
  const data = [];

  if (category === "Government & Legal") return [];

  for (let i = 1; i <= daysInMonth; i++) {
    const currentDay = new Date(date.getFullYear(), date.getMonth(), i);

    const isHighSpend = Math.random() > 0.8;
    const spent = isHighSpend
      ? Math.floor(Math.random() * 300)
      : Math.floor(Math.random() * 50);

    const allocated = Math.floor(Math.random() * 100) + 100;

    data.push({
      day: formatDate(currentDay),
      spent: spent,
      allocated: allocated,
    });
  }
  return data;
};

export const useSpendingPage = () => {
  const { data: user } = useGetUser();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const accountCreatedAt = useMemo(() => {
    return user?.createdAt ? new Date(user.createdAt) : new Date("2024-01-01");
  }, [user]);

  const handleDateChange = (newDate) => {
    setIsLoading(true);
    setSelectedDate(newDate);
  };

  const handleCategoryChange = (newCategory) => {
    setIsLoading(true);
    setSelectedCategory(newCategory);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      const data = generateDailyData(selectedDate, selectedCategory);
      setChartData(data);
      setIsLoading(false);
    }, 600);

    return () => clearTimeout(timer);
  }, [selectedDate, selectedCategory]);

  return {
    selectedDate,
    setSelectedDate: handleDateChange,
    selectedCategory,
    setSelectedCategory: handleCategoryChange,
    chartData,
    isLoading,
    accountCreatedAt,
    formatDate,
  };
};
