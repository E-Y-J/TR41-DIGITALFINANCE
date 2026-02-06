import { useState } from "react";
import { Box, Tooltip, IconButton, CircularProgress } from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import BarChartIcon from "@mui/icons-material/BarChart";
import PieChartIcon from "@mui/icons-material/PieChart";
import DashboardWidget from "../../components/common/DashboardWidget";
import DashboardBarChart from "./components/DashboardBarChart";
import DashboardPieChart from "./components/DashboardPieChart";
import { useDailyBreakdown } from "../../hooks/useDailyBreakdown";
import {
  getDefaultFirstDayOfMonth,
  getTodayISODate,
} from "../../utils/constants";

const BudgetWidget = () => {
  const navigate = useNavigate();
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

  const { dailyCategoryData, isFetching, isLoading } = useDailyBreakdown(
    getDefaultFirstDayOfMonth(),
    getTodayISODate(),
  );

  console.log("BudgetWidget - dailyCategoryData:", dailyCategoryData);

  const headerActions = (
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

      <Tooltip title="View Summary">
        <IconButton
          onClick={() => navigate("/home/budget")}
          sx={getButtonStyle(viewGraph === "summary")}
        >
          <ArrowForwardIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );

  if (isLoading) {
    return (
      <DashboardWidget title="My Monthly Spending" sx={{ minHeight: 450 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            width: "100%",
          }}
        >
          <CircularProgress size={50} thickness={4.5} />
        </Box>
      </DashboardWidget>
    );
  }

  return (
    <DashboardWidget title="My Monthly Spending" action={headerActions}>
      <Box
        sx={{
          mt: 1,
          height: "100%",
          width: "100%",
          position: "relative",
          transition: "opacity 0.3s ease-in-out",
          opacity: isFetching ? 0.4 : 1,
          pointerEvents: isFetching ? "none" : "auto",
        }}
      >
        {viewGraph === "graph" ? (
          <DashboardBarChart data={dailyCategoryData} />
        ) : (
          <DashboardPieChart data={dailyCategoryData} />
        )}
      </Box>
    </DashboardWidget>
  );
};

export default BudgetWidget;
