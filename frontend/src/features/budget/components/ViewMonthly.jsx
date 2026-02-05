import { Box, Typography, Paper } from "@mui/material";
import SpendingFilters from "./BudgetFilters";
import MonthlyLineChart from "./MonthlyLineChart";

const ViewMonthly = ({
  selectedCategory,
  setSelectedCategory,
  selectedDate,
  setSelectedDate,
  accountCreatedAt,
  chartData,
  isLoading,
}) => {
  const headerDate = new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
  }).format(selectedDate);

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
        <Box>
          <Typography
            variant="h6"
            component="h2"
            fontWeight={700}
            lineHeight={1.2}
          >
            Monthly Spending Since: {headerDate}
          </Typography>
        </Box>

        <Box sx={{ width: { xs: "100%", md: "auto" } }}>
          <SpendingFilters
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            selectedDate={selectedDate}
            setSelectedDate={setSelectedDate}
            accountCreatedAt={accountCreatedAt}
            viewType="monthly"
          />
        </Box>
      </Box>

      <Box>
        <MonthlyLineChart
          selectedDate={selectedDate}
          data={chartData}
          isLoading={isLoading}
        />
      </Box>
    </Paper>
  );
};

export default ViewMonthly;
