import { Box, Typography, Button, Paper } from "@mui/material";
import DashboardLayout from "../layouts/DashboardLayout";
import TransactionTable from "../components/dashboard/TransactionTable";

const MockChartPlaceholder = ({ height = 100, text }) => (
  <Box
    sx={{
      height: height,
      bgcolor: "grey.100",
      borderRadius: 2,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      border: "1px dashed",
      borderColor: "grey.400",
      width: "100%",
    }}
  >
    <Typography color="text.secondary">{text}</Typography>
  </Box>
);

export default function HomePage() {
  return (
    <DashboardLayout>
      <Box sx={{ bgcolor: "background.default", p: 1, minHeight: "100vh" }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Welcome, User
        </Typography>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              md: "1fr 1fr 1fr",
            },
            gap: 3,
          }}
        >
          <Box sx={{ gridColumn: { md: "span 2" } }}>
            <Paper sx={{ p: 3, height: "100%" }} variant="outlined">
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                My Cards
              </Typography>
              <MockChartPlaceholder height={220} text="Credit Cards" />
            </Paper>
          </Box>
          <Box sx={{ gridColumn: { md: "span 1" } }}>
            <Paper
              sx={{
                p: 3,
                height: "100%",
                bgcolor: "primary.light",
                color: "white",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
              variant="outlined"
            >
              <Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>
                  AI Insights
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Spending is 15% higher this week.
                </Typography>
              </Box>
              <MockChartPlaceholder height={120} text="AI Graph" />
            </Paper>
          </Box>
          <Box sx={{ gridColumn: { md: "span 1" } }}>
            <Paper sx={{ p: 3, height: "100%" }} variant="outlined">
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                Something else
              </Typography>
              <MockChartPlaceholder height={250} text="Pie Chart" />
            </Paper>
          </Box>
          <Box sx={{ gridColumn: { md: "span 2", lg: "span 2" } }}>
            <Paper
              sx={{
                p: 2,
                display: "flex",
                flexDirection: "column",
                borderRadius: 4,

                height: { xs: "auto", md: "100%" },
                maxHeight: { xs: "none", md: 400 },
              }}
              variant="outlined"
            >
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  mb: 1,
                  px: 1,
                }}
              >
                <Typography variant="h6" fontWeight="bold">
                  Transaction History
                </Typography>
                <Button size="small">View All</Button>
              </Box>
              <TransactionTable />
            </Paper>
          </Box>
        </Box>
      </Box>
    </DashboardLayout>
  );
}
