import { Box, Typography, Container, Paper } from "@mui/material";

import SpendingFilters from "../features/spending/components/SpendingFilters";
import DailySpendingChart from "../features/spending/components/DailySpendingChart";

import { useSpendingPage } from "../hooks/useSpendingPage";

const BudgetPage = () => {
  const {
    selectedDate,
    setSelectedDate,
    selectedCategory,
    setSelectedCategory,
    chartData,
    isLoading,
    accountCreatedAt,
  } = useSpendingPage();

  const headerDate = new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
  }).format(selectedDate);

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          fontWeight={800}
          sx={{ letterSpacing: "-0.5px", color: "text.primary" }}
        >
          Spending Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Deep dive into your daily spending habits vs. your allocated budget.
        </Typography>
      </Box>

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
              Daily Spending vs. Budget
            </Typography>

            <Typography variant="body2" color="text.secondary">
              {headerDate}
            </Typography>
          </Box>

          <Box sx={{ width: { xs: "100%", md: "auto" } }}>
            <SpendingFilters
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
              accountCreatedAt={accountCreatedAt}
            />
          </Box>
        </Box>
        <Box>
          <DailySpendingChart
            selectedDate={selectedDate}
            data={chartData}
            isLoading={isLoading}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default BudgetPage;
