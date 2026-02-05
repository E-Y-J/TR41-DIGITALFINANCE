import { Box, Paper, Typography, CircularProgress, Fade } from "@mui/material";
import SpendingFilters from "./BudgetFilters";
import DailyBarChart from "./DailyBarChart";
import EmptyTrendView from "../../../components/common/EmptyTrendView";
import { formatDate } from "../../../utils/constants";

const ViewDay = ({
  specificCategory,
  setSpecificCategory,
  specificDate,
  setSpecificDate,
  accountCreatedAt,
  dailyCategoryData,
  isLoading,
  isFetching,
}) => {
  const getHeaderText = (date) => {
    if (!date) return "Select a Date";

    const today = new Date().toDateString();
    const isToday = date.toDateString() === today;

    return isToday
      ? `Today's Expenses (${formatDate(date)})`
      : `Expenses for ${formatDate(date)}`;
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
      {!specificDate ? (
        <EmptyTrendView
          header="Visualize Your Daily Expenses"
          text="Pick a date to see your spending for that day."
        />
      ) : isLoading ? (
        <Box sx={{ p: 6, textAlign: "center" }}>
          <CircularProgress size={40} />
        </Box>
      ) : (
        <Fade in={!!specificDate} timeout={500}>
          <Box
            sx={{
              position: "relative",
              opacity: isFetching ? 0.4 : 1,
              transition: "opacity 0.2s ease",
              pointerEvents: isFetching ? "none" : "auto",
            }}
          >
            <DailyBarChart
              data={dailyCategoryData}
              specificCategory={specificCategory}
            />
          </Box>
        </Fade>
      )}
    </Paper>
  );
};

export default ViewDay;
