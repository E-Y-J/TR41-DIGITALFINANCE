import { Box, Typography } from "@mui/material";
import { useGetUser } from "../features/auth/useGetUser";

import AiInsightsWidget from "../features/ai-insights/AiInsightsWidget";
import SpendingWidget from "../features/spending/SpendingWidget";
import RecentTransactionsWidget from "../features/transactions/RecentTransactionsWidget";
import ActiveLoansWidget from "../features/loans/ActiveLoansWidget";

export default function HomePage() {
  const { data: user } = useGetUser();

  return (
    <Box
      sx={{
        bgcolor: "background.default",
        p: { xs: 2, md: 3 },
        minHeight: "100vh",
      }}
    >
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Welcome, {user?.first_name || "User"}
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "repeat(3, 1fr)",
          },
          gap: 3,
          mb: 3,
        }}
      >
        {/* AI Insights */}
        <Box sx={{ gridColumn: { md: "span 1" } }}>
          <AiInsightsWidget />
        </Box>

        {/* Spending Charts */}
        <Box sx={{ gridColumn: { md: "span 2" } }}>
          <SpendingWidget />
        </Box>

        {/* Recent Transactions */}
        <Box sx={{ gridColumn: { md: "span 2" } }}>
          <RecentTransactionsWidget />
        </Box>

        {/* Active Loans */}
        <Box sx={{ gridColumn: { md: "span 1" } }}>
          <ActiveLoansWidget />
        </Box>
      </Box>
    </Box>
  );
}
