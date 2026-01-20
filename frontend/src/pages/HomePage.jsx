import { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Paper,
  Tooltip,
  IconButton,
} from "@mui/material";
import TransactionTable from "../components/dashboard/TransactionTable";
import LoanTracker from "../components/dashboard/LoanTracker";
import BudgetBarChart from "../components/dashboard/MonthlyTracker";
import SpendingPie from "../components/dashboard/PieChart";
import { useGetUser } from "../hooks/queries/useGetUser";

import BarChartIcon from "@mui/icons-material/BarChart";
import PieChartIcon from "@mui/icons-material/PieChart";

export default function HomePage() {
  const { data: user } = useGetUser();
  const [viewGraph, setViewGraph] = useState("graph");

  const getButtonStyle = (isActive) => ({
    color: isActive ? "#ffffff" : "text.secondary",
    bgcolor: isActive ? "primary.main" : "transparent",
    border: "1px solid",
    borderColor: isActive ? "primary.main" : "grey.300",
    borderRadius: 2,
    p: 1,

    "&:hover": {
      bgcolor: isActive ? "primary.main" : "grey.100",

      borderColor: isActive ? "primary.main" : "grey.400",
    },
  });

  return (
    <Box sx={{ bgcolor: "background.default", p: 1, minHeight: "100vh" }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Welcome, {user?.first_name || "User"}
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "1fr 1fr 1fr",
          },
          gap: 3,
          mb: 3,
        }}
      >
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
                To be implemented with AI summary of your spending habits.
              </Typography>
            </Box>
          </Paper>
        </Box>
        <Box sx={{ gridColumn: { md: "span 2" } }}>
          <Paper
            elevation={3}
            sx={{
              p: { xs: 2, sm: 3 },
              display: "flex",
              flexDirection: "column",
              borderRadius: 4,
              border: "1px solid",
              borderColor: "grey.200",
              height: "100%",
              minHeight: 400,
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                alignItems: { xs: "flex-start", sm: "center" },
                justifyContent: "space-between",
                gap: 2,
                mb: 3,
              }}
            >
              <Typography variant="h6" fontWeight="bold">
                My Monthly Spending
              </Typography>

              <Box sx={{ display: "flex", gap: 1 }}>
                <Tooltip title="View Bar Chart">
                  <IconButton
                    onClick={() => setViewGraph("graph")}
                    sx={getButtonStyle(viewGraph === "graph")}
                  >
                    <BarChartIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="View Pie Chart">
                  <IconButton
                    onClick={() => setViewGraph("pie")}
                    sx={getButtonStyle(viewGraph === "pie")}
                  >
                    <PieChartIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            <Box sx={{ mt: 1, flexGrow: 1, position: "relative" }}>
              {viewGraph === "graph" ? <BudgetBarChart /> : <SpendingPie />}
            </Box>
          </Paper>
        </Box>

        <Box sx={{ gridColumn: { md: "span 2", lg: "span 2" } }}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              display: "flex",
              flexDirection: "column",
              borderRadius: 4,
              height: { xs: "auto", md: 450 },
              border: "1px solid",
              borderColor: "grey.200",
            }}
          >
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 1.5,
              }}
            >
              <Typography variant="h6" fontWeight={700}>
                Transaction History
              </Typography>
              <Button
                size="small"
                sx={{
                  textTransform: "none",
                  fontWeight: 600,
                  borderRadius: 2,
                }}
              >
                View All
              </Button>
            </Box>

            <Box sx={{ flexGrow: 1, overflow: "hidden" }}>
              <TransactionTable />
            </Box>
          </Paper>
        </Box>

        <Box sx={{ gridColumn: { md: "span 1" } }}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              height: { xs: "auto", md: 450 },
              display: "flex",
              flexDirection: "column",
              borderRadius: 4,
              border: "1px solid",
              borderColor: "grey.200",
            }}
          >
            <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
              Active Loans
            </Typography>

            <Box sx={{ flexGrow: 1 }}>
              <LoanTracker />
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
