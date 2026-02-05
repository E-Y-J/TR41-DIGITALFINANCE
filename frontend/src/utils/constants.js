export const CATEGORIES = [
  "Food & Dining",
  "Transportation",
  "Shopping & Retail",
  "Entertainment & Recreation",
  "Healthcare & Medical",
  "Utilities & Services",
  "Financial Services",
  "Income",
  "Government & Legal",
  "Charity & Donations",
];

export const CATEGORY_COLORS = {
  "Food & Dining": "#FF7043",
  Transportation: "#AB47BC",
  "Shopping & Retail": "#26A69A",
  "Entertainment & Recreation": "#FFA726",
  "Healthcare & Medical": "#EF5350",
  "Utilities & Services": "#42A5F5",
  "Financial Services": "#7E57C2",
  Income: "#66BB6A",
  "Government & Legal": "#78909C",
  "Charity & Donations": "#EC407A",
};

export const getCategoryColor = (categoryName) => {
  return CATEGORY_COLORS[categoryName] || "#BDBDBD";
};

export const formatDate = (dateInput, viewType = "daily") => {
  if (!dateInput) return "";

  const date =
    dateInput instanceof Date
      ? dateInput
      : new Date(dateInput.replace(/-/g, "/"));

  if (isNaN(date.getTime())) return "";

  if (viewType === "monthly") {
    return date.toLocaleDateString("en-US", {
      month: "long",
      year: "numeric",
    });
  }

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

export const getLocalISODate = (dateInput, viewType = "daily") => {
  if (!dateInput) return "";

  const date =
    dateInput instanceof Date
      ? dateInput
      : new Date(dateInput.replace(/-/g, "/"));

  if (isNaN(date.getTime())) return "";

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return viewType === "daily" ? `${year}-${month}-${day}` : `${year}-${month}`;
};
