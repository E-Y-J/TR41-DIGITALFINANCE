import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme } from "@mui/material/styles";
import { Box, useMediaQuery, alpha } from "@mui/material";
import { useMemo } from "react";

const MonthlyLineChart = ({ data = [] }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const { maxDataPoint, gradientOffsets } = useMemo(() => {
    if (!data.length) return { maxDataPoint: 2000, gradientOffsets: {} };

    const budgetLimit = data[data.length - 1].allocated;
    const maxSpent = Math.max(...data.map((d) => d.spent));

    const max = Math.max(maxSpent, budgetLimit) * 1.25;

    return {
      maxDataPoint: max,
      gradientOffsets: {
        danger: (1 - budgetLimit / max) * 100,
        warning: (1 - (budgetLimit * 0.85) / max) * 100,
        safe: (1 - (budgetLimit * 0.5) / max) * 100,
      },
    };
  }, [data]);

  return (
    <Box sx={{ width: "100%", height: isMobile ? 350 : 500 }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="financeTrendGradient" x1="0" y1="0" x2="0" y2="1">
            {/* TOP: Critical zone - use a very bright red/pink */}
            <stop
              offset="0%"
              stopColor={theme.palette.error.light}
              stopOpacity={1}
            />

            {/* MID-TOP: Danger transition */}
            <stop
              offset={`${gradientOffsets.danger}%`}
              stopColor={theme.palette.error.main}
              stopOpacity={0.9}
            />

            {/* MIDDLE: Warning zone - vibrant orange */}
            <stop
              offset={`${gradientOffsets.warning}%`}
              stopColor={theme.palette.warning.light}
              stopOpacity={0.8}
            />

            {/* MID-BOTTOM: Safe zone - sky blue rather than deep blue */}
            <stop
              offset={`${gradientOffsets.safe}%`}
              stopColor={theme.palette.info.light}
              stopOpacity={0.6}
            />

            {/* BOTTOM: Deep Fade - pure transparency */}
            <stop
              offset="100%"
              stopColor={theme.palette.info.main}
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
      </svg>
      <LineChart
        dataset={data}
        margin={{
          top: 40,
          right: isMobile ? 20 : 40,
          bottom: 60,
          left: isMobile ? 20 : 40,
        }}
        xAxis={[
          {
            scaleType: "point",
            dataKey: "month",
            valueFormatter: (val) => (isMobile ? val.split(" ")[0] : val),
          },
        ]}
        yAxis={[
          {
            max: maxDataPoint,
            valueFormatter: (val) => `$${(val / 1000).toFixed(1)}k`,
          },
        ]}
        series={[
          {
            id: "spending-series",
            dataKey: "spent",
            label: "Spent",
            area: true,
            curve: "monotoneX",
            color: "url(#financeTrendGradient)",
            showMark: false,
            disableMark: true,
          },
          {
            id: "budget-limit",
            dataKey: "allocated",
            label: "Budget",
            color: theme.palette.text.disabled,
            curve: "step",
            strokeDashArray: "8 4",
            showMark: false,
            disableMark: true,
          },
        ]}
        sx={{
          "& .MuiAreaElement-series-spending-series": {
            fillOpacity: isDarkMode ? 0.5 : 0.3,
          },
          "& .MuiLineElement-series-spending-series": {
            strokeWidth: 4,
            filter: isDarkMode
              ? `drop-shadow(0px 0px 12px ${alpha(theme.palette.primary.main, 0.8)})`
              : "none",
          },
          "& .MuiMarkElement-root": {
            stroke: isDarkMode ? theme.palette.background.paper : "#fff",
            strokeWidth: 2,
            scale: "1.2",
          },
          "& .MuiChartsGrid-line": {
            stroke: alpha(theme.palette.divider, 0.3),
            strokeDasharray: "4 4",
          },
          "& .MuiLineElement-series-budget-limit": {
            stroke: alpha(theme.palette.text.disabled, 0.5),
            strokeWidth: 2,
            strokeDasharray: "10 5",
          },
        }}
      />
    </Box>
  );
};

export default MonthlyLineChart;
