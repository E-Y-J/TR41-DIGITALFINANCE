import { Box, Paper, Typography } from "@mui/material";
import SpendingFilters from "./BudgetFilters";
import DailyBarChart from "./DailyBarChart";

const ViewDay = ({
  specificCategory,
  setSpecificCategory,
  specificDate,
  setSpecificDate,
  accountCreatedAt,
  dailyCategoryData,
  isLoading,
}) => {
  const getHeaderText = (date) => {
    if (!date) return "Select a Date";

    const today = new Date().toDateString();
    const isToday = date.toDateString() === today;

    const formattedDate = date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });

    return isToday
      ? `Today's Expenses (${formattedDate})`
      : `Expenses for ${formattedDate}`;
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: { xs: 2, sm: 3 },
        borderRadius: 4,
        border: "1px solid",
        borderColor: "grey.200",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box
        sx={{
          mb: 3,
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          alignItems: { xs: "flex-start", md: "center" },
          justifyContent: "space-between",
          gap: 2,
        }}
      >
        <Typography variant="h6">{getHeaderText(specificDate)}</Typography>
        <SpendingFilters
          selectedDate={specificDate}
          setSelectedDate={setSpecificDate}
          selectedCategory={specificCategory}
          setSelectedCategory={setSpecificCategory}
          accountCreatedAt={accountCreatedAt}
          viewType="daily"
        />
      </Box>

      <DailyBarChart
        data={dailyCategoryData}
        specificCategory={specificCategory}
        isLoading={isLoading}
        hasSelectedDate={!!specificDate}
      />
    </Paper>
  );
};

export default ViewDay;
