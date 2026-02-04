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

export const transformDataForPie = (currentData) => {
  return currentData.flatMap((item) => {
    const color = getCategoryColor(item.category);
    const safeSpent = Math.min(item.spent, item.allocated);
    const remaining = Math.max(0, item.allocated - item.spent);

    return [
      {
        id: `${item.category}-spent`,
        label: item.category,
        value: safeSpent,
        color: color,
        fullAllocated: item.allocated,
        fullSpent: item.spent,
        isSpent: true,
      },
      {
        id: `${item.category}-left`,
        label: item.category,
        value: remaining,
        color: alpha(color, 0.2),
        fullAllocated: item.allocated,
        fullSpent: item.spent,
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
