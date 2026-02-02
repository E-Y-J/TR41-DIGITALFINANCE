import { Box, Typography, Container, CircularProgress } from "@mui/material";

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
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Spending Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Deep dive into your daily spending habits vs. your allocated budget.
        </Typography>
      </Box>

      <SpendingFilters
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        selectedDate={selectedDate}
        setSelectedDate={setSelectedDate}
        accountCreatedAt={accountCreatedAt}
      />

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          {selectedCategory} Spending: {headerDate}
        </Typography>

        {isLoading ? (
          <Box sx={{ display: "flex", justifyContent: "center", p: 10 }}>
            <CircularProgress />
          </Box>
        ) : (
          <DailySpendingChart data={chartData} isLoading={isLoading} />
        )}
      </Box>
    </Container>
  );
};

export default BudgetPage;
