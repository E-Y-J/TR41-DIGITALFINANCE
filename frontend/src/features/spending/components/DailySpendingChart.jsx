import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme } from "@mui/material/styles";
import { Box, useMediaQuery } from "@mui/material";

import EmptyState from "../../../components/common/EmptyState";

const DailySpendingChart = ({ data, isLoading }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  if (!isLoading && (!data || data.length === 0)) {
    return (
      <EmptyState
        header="No Transactions Found"
        text="We couldn't find any transactions matching your filters. Try adjusting your date or category."
      />
    );
  }

  const chartHeight = isMobile ? 350 : 500;

  const chartMargin = {
    top: 10,
    right: isMobile ? 10 : 30,
    bottom: 20,
    left: isMobile ? 10 : 30,
  };

  return (
    <Box sx={{ width: "100%", height: chartHeight }}>
      <svg width={0} height={0}>
        <defs>
          <linearGradient id="lineTemperature" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stopColor="#2196f3" />
            <stop offset="50%" stopColor="#9c27b0" />
            <stop offset="100%" stopColor="#f44336" />
          </linearGradient>

          <linearGradient id="areaTemperature" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stopColor="#2196f3" stopOpacity={0.3} />
            <stop offset="50%" stopColor="#9c27b0" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#f44336" stopOpacity={0.3} />
          </linearGradient>
        </defs>
      </svg>

      <LineChart
        dataset={data}
        margin={chartMargin}
        grid={{ vertical: true, horizontal: true }}
        axisHighlight={{ x: "line" }}
        xAxis={[
          {
            scaleType: "point",
            dataKey: "day",
            label: "",
            tickLabelStyle: { display: "none" },
          },
        ]}
        yAxis={[
          {
            label: isMobile ? "" : "Amount ($)",
            valueFormatter: (value) => `$${value}`,
            tickLabelStyle: {
              fontSize: isMobile ? 10 : 12,
              fill: theme.palette.text.secondary,
            },
          },
        ]}
        series={[
          {
            id: "spent",
            dataKey: "spent",
            label: "Spent",
            valueFormatter: (value) => `$${value}`,
            color: "#2196f3",
            showMark: false,
            curve: "natural",
            area: true,
            connectNulls: true,
            disableHighlight: false,
          },
          {
            id: "allocated",
            dataKey: "allocated",
            label: "Allocated",
            valueFormatter: (value) => `$${value}`,
            color: theme.palette.text.secondary,
            showMark: false,
            curve: "step",
            disableHighlight: true,
          },
        ]}
        sx={{
          "& .MuiAreaElement-series-spent": {
            fill: "url(#areaTemperature)",
          },
          "& .MuiLineElement-series-spent": {
            stroke: "url(#lineTemperature)",
            strokeWidth: 4,
          },
        }}
        slotProps={{
          legend: {
            hidden: false,
            position: {
              vertical: "top",
              horizontal: isMobile ? "middle" : "right",
            },
            padding: 0,
            itemMarkWidth: 10,
            itemMarkHeight: 10,
            labelStyle: {
              fontSize: isMobile ? 12 : 12,
            },
          },
        }}
      />
    </Box>
  );
};

export default DailySpendingChart;
