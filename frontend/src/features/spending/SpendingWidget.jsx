import { useState } from "react";
import { Box, Tooltip, IconButton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import BarChartIcon from "@mui/icons-material/BarChart";
import PieChartIcon from "@mui/icons-material/PieChart";
import DashboardWidget from "../../components/common/DashboardWidget";
import BudgetBarChart from "./components/BudgetBarChart";
import BudgetBreakdownPie from "./components/BudgetBreakdownPie";

const SpendingWidget = () => {
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

  return (
    <DashboardWidget title="My Monthly Spending" action={headerActions}>
      <Box sx={{ mt: 1, height: "100%", width: "100%" }}>
        {viewGraph === "graph" ? <BudgetBarChart /> : <BudgetBreakdownPie />}
      </Box>
    </DashboardWidget>
  );
};

export default SpendingWidget;
