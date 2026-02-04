import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme } from "@mui/material/styles";
import { Box, useMediaQuery } from "@mui/material";
import EmptyState from "../../../components/common/EmptyState";

const MonthlyLineChart = ({ data, isLoading }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  if (!isLoading && (!data || data.length === 0)) {
    return (
      <EmptyState
        header="No Transactions Found"
        text="We couldn't find any transactions matching your filters."
      />
    );
  }

  return (
    <Box sx={{ width: "100%", height: isMobile ? 350 : 500 }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="dynamicAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f44336" stopOpacity={0.9} />
            <stop offset="20%" stopColor="#ff9800" stopOpacity={0.7} />
            <stop offset="50%" stopColor="#2196f3" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#2196f3" stopOpacity={0.1} />
          </linearGradient>
        </defs>
      </svg>

      <LineChart
        dataset={data}
        margin={{
          top: 20,
          right: isMobile ? 20 : 40,
          bottom: 60,
          left: isMobile ? 10 : 60,
        }}
        grid={{ horizontal: true }}
        xAxis={[
          {
            scaleType: "point",
            dataKey: "month",
            valueFormatter: (value) => {
              const date = new Date(value + "-01T00:00:00");
              return date.toLocaleString("default", {
                month: "short",
                year: isMobile ? "2-digit" : "numeric",
              });
            },
          },
        ]}
        yAxis={[{ label: isMobile ? "" : "Total Spent ($)" }]}
        series={[
          {
            id: "spending-series",
            dataKey: "spent",
            label: "Actual Spending",
            area: true,
            curve: "monotoneX",
            showMark: true,
          },
          {
            id: "budget-limit",
            dataKey: "allocated",
            label: "Budget Limit",
            color: theme.palette.text.disabled,
            curve: "stepAfter",
            strokeDashArray: "5 5",
            showMark: true,
          },
        ]}
        sx={{
          "& .MuiAreaElement-series-spending-series": {
            fill: "url(#dynamicAreaGradient)",
          },
          "& .MuiLineElement-series-spending-series": {
            stroke: "url(#dynamicAreaGradient)",
            strokeWidth: 4,
          },
          "& .MuiMarkElement-series-spending-series": {
            fill: "url(#dynamicAreaGradient)",
            stroke: "#ffffff",
            strokeWidth: 2,
            r: isMobile ? 3 : 4,
          },
        }}
      />
    </Box>
  );
};

export default MonthlyLineChart;
