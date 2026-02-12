import { useState } from "react";
import {
  Box,
  Tooltip,
  IconButton,
  CircularProgress,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import BarChartIcon from "@mui/icons-material/BarChart";
import PieChartIcon from "@mui/icons-material/PieChart";
import DashboardWidget from "../../components/common/DashboardWidget";
import DashboardBarChart from "./components/DashboardBarChart";
import DashboardPieChart from "./components/DashboardPieChart";
import { useBudgetSuggestions } from "./useBudgetSuggestions";
import { useDailyBreakdown } from "../../hooks/useDailyBreakdown";
import {
  getDefaultFirstDayOfMonth,
  getTodayISODate,
} from "../../utils/constants";

const BudgetWidget = () => {
  const navigate = useNavigate();
  const [viewGraph, setViewGraph] = useState("graph");

  const getButtonStyle = (isActive) => ({
    color: isActive ? "primary.contrastText" : "text.secondary",
    bgcolor: isActive ? "primary.main" : "transparent",
    border: "1px solid",
    borderColor: isActive ? "primary.main" : "grey.300",
    borderRadius: 2,
    p: 1,
    "&:hover": {
      bgcolor: isActive ? "primary.main" : "action.hover",
      borderColor: isActive ? "primary.main" : "grey.400",
    },
  });

  const { dailyCategoryData, isFetching, isLoading } = useDailyBreakdown(
    getDefaultFirstDayOfMonth(),
    getTodayISODate(),
  );

  const {
    data: suggestionData,
    isLoading: loadingSuggestions,
    isFetching: fetchingSuggestions,
  } = useBudgetSuggestions(3);

  const renderAnalysisPeriod = () => {
    if (!suggestionData?.analysis) return null;
    const { start_date, end_date } = suggestionData.analysis;

    const start = new Date(start_date + "T00:00:00").toLocaleDateString(
      "en-US",
      { month: "short", year: "numeric" },
    );
    const end = new Date(end_date + "T00:00:00").toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    });

    return `AI suggestions based on spending from ${start} — ${end}`;
  };

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

  if (isLoading || loadingSuggestions) {
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
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
        {suggestionData?.analysis && (
          <Typography
            variant="caption"
            color="text.disabled"
            sx={{
              mb: 1,
              fontStyle: "italic",
              display: "block",
              opacity: isFetching || fetchingSuggestions ? 0.4 : 1,
            }}
          >
            {renderAnalysisPeriod()}
          </Typography>
        )}

        <Box
          sx={{
            flexGrow: 1,
            width: "100%",
            position: "relative",
            transition: "opacity 0.3s ease-in-out",
            opacity: isFetching || fetchingSuggestions ? 0.4 : 1,
            pointerEvents: isFetching || fetchingSuggestions ? "none" : "auto",
          }}
        >
          {viewGraph === "graph" ? (
            <DashboardBarChart
              data={dailyCategoryData}
              suggestions={suggestionData.suggestions}
            />
          ) : (
            <DashboardPieChart
              data={dailyCategoryData}
              suggestions={suggestionData.suggestions}
            />
          )}
        </Box>
      </Box>
    </DashboardWidget>
  );
};

export default BudgetWidget;
