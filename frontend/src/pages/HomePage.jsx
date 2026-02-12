import { Box, Typography } from "@mui/material";
import { useGetUser } from "../features/auth/useGetUser";

import AiInsightsWidget from "../features/ai-insights/AiInsightsWidget";
import BudgetWidget from "../features/budget/BudgetWidget";
import RecentTransactionsWidget from "../features/transactions/RecentTransactionsWidget";
import ActiveLoansWidget from "../features/loans/ActiveLoansWidget";

export default function HomePage() {
  const { data: user } = useGetUser();

  return (
    <Box
      sx={{
        p: { xs: 2, md: 3 },
        width: "100%",
        maxWidth: "100%",
        boxSizing: "border-box",
        overflowX: "hidden",
      }}
    >
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Welcome, {user?.nickname || user?.first_name || "User"}
      </Typography>

      <Box
        sx={{
          display: "grid",
          width: "100%",
          gridTemplateColumns: {
            xs: "1fr",
            md: "repeat(3, 1fr)",
          },
          gap: { xs: 2, md: 3 },
          mb: 3,

          "& > div": {
            minWidth: 0,
            overflow: "hidden",
          },
        }}
      >
        <Box sx={{ gridColumn: { md: "span 2" } }}>
          <BudgetWidget />
        </Box>

        <Box sx={{ gridColumn: { md: "span 1" } }}>
          <ActiveLoansWidget />
        </Box>

        <Box sx={{ gridColumn: { md: "span 1" } }}>
          <AiInsightsWidget />
        </Box>

        <Box sx={{ gridColumn: { md: "span 2" } }}>
          <RecentTransactionsWidget />
        </Box>
      </Box>
    </Box>
  );
}
