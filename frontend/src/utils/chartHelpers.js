import { alpha } from "@mui/material/styles";
import { CATEGORIES, getCategoryColor } from "./constants";

export const formatCurrency = (value) => `$${value.toLocaleString()}`;

export const getMonthYearOptions = (userStartYear) => {
  const options = [];
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  for (let year = currentYear; year >= userStartYear; year--) {
    const startMonth = year === currentYear ? currentMonth : 11;

    for (let month = startMonth; month >= 0; month--) {
      const date = new Date(year, month);
      const label = date.toLocaleString("default", {
        month: "short",
        year: "numeric",
      });
      const value = `${year}-${String(month + 1).padStart(2, "0")}`;

      options.push({ label, value });
    }
  }
  return options;
};

export const getDefaultMonth = () => {
  const d = new Date();
  d.setMonth(d.getMonth() - 1);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return `${d.getFullYear()}-${month}`;
};
export const generateChartData = () => {
  return CATEGORIES.map((cat) => ({
    category: cat,
    allocated: Math.floor(Math.random() * 500) + 200,
    spent: Math.floor(Math.random() * 500) + 100,
  }));
};

const getCategoryMetrics = (cat, spendingData, suggestionsInput = []) => {
  const rawSpending = spendingData?.[0] || {};

  const suggestionsArray = Array.isArray(suggestionsInput)
    ? suggestionsInput
    : suggestionsInput?.suggestions || [];

  const suggestion = suggestionsArray.find((s) => s.category_name === cat);

  const spent = parseFloat(rawSpending[cat] || 0);

  const suggested = suggestion?.suggested_amount
    ? parseFloat(suggestion.suggested_amount)
    : 0;

  return {
    spent,
    allocated: suggested || 0,
  };
};

export const transformDataForBar = (data, suggestions = []) => {
  if (!data || data.length === 0) return [];

  return CATEGORIES.map((cat) => {
    const { spent, allocated } = getCategoryMetrics(cat, data, suggestions);

    return {
      category: cat,
      spent,
      allocated,
    };
  });
};

export const transformDataForPie = (data, suggestions = []) => {
  if (!data || data.length === 0) return [];

  return CATEGORIES.slice(0, 10).flatMap((cat) => {
    const { spent, allocated } = getCategoryMetrics(cat, data, suggestions);

    const displayAllocated = allocated || 100;
    const color = getCategoryColor(cat);
    const safeSpent = Math.min(spent, displayAllocated);
    const remaining = Math.max(0, displayAllocated - spent);

    return [
      {
        id: `${cat}-spent`,
        label: cat,
        value: safeSpent,
        color: color,
        fullAllocated: displayAllocated,
        fullSpent: spent,
        isSpent: true,
      },
      {
        id: `${cat}-left`,
        label: cat,
        value: remaining,
        color: alpha(color, 0.2),
        fullAllocated: displayAllocated,
        fullSpent: spent,
        isSpent: false,
      },
    ];
  });
};

export const getPieLabelFormatter = (item, isMobile) => {
  const percent = Math.round((item.fullSpent / item.fullAllocated) * 100);
  const remaining = Math.max(0, item.fullAllocated - item.fullSpent);

  if (isMobile) {
    if (item.isSpent) return `${formatCurrency(item.fullSpent)} (${percent}%)`;
    return `${formatCurrency(remaining)} left`;
  }

  const spentStr = formatCurrency(item.fullSpent);
  const totalStr = formatCurrency(item.fullAllocated);

  if (item.isSpent) return `${spentStr} of ${totalStr} (${percent}%)`;
  return `${formatCurrency(remaining)} remaining (${100 - percent}%)`;
};
