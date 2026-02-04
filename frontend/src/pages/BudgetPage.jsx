import { Box, Typography } from "@mui/material";

import ViewMonthly from "../features/budget/components/ViewMonthly";
import ViewDay from "../features/budget/components/ViewDay";

import { useMonthlySpending } from "../hooks/useMonthlySpending";
import { useDailyBreakdown } from "../hooks/useDailyBreakdown";
import { useGetUser } from "../features/auth/useGetUser";

const BudgetPage = () => {
  const monthly = useMonthlySpending();
  const daily = useDailyBreakdown();
  const { data: user } = useGetUser();

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

      <Box sx={{ mb: 5 }}>
        <ViewMonthly
          selectedCategory={monthly.selectedCategory}
          setSelectedCategory={monthly.setSelectedCategory}
          selectedDate={monthly.selectedDate}
          setSelectedDate={monthly.setSelectedDate}
          accountCreatedAt={
            user?.created_at ? new Date(user.created_at) : new Date()
          }
          chartData={monthly.chartData}
          isLoading={monthly.isLoading}
        />
      </Box>
      <Box sx={{ mb: 5 }}>
        <ViewDay
          specificDate={daily.specificDate}
          setSpecificDate={daily.setSpecificDate}
          specificCategory={daily.specificCategory}
          setSpecificCategory={daily.setSpecificCategory}
          accountCreatedAt={
            user?.created_at ? new Date(user.created_at) : new Date()
          }
          dailyCategoryData={daily.dailyCategoryData}
          isLoading={daily.isLoading}
        />
      </Box>
    </Box>
  );
};

export default BudgetPage;
