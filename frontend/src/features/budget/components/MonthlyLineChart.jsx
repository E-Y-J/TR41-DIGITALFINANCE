import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme } from "@mui/material/styles";
import { Box, useMediaQuery, alpha } from "@mui/material";
import { useMemo } from "react";

const MonthlyLineChart = ({ data = [] }) => {
  const theme = useTheme();
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
            <stop offset="0%" stopColor={theme.palette.error.main} />
            <stop
              offset={`${gradientOffsets.danger}%`}
              stopColor={theme.palette.error.light}
            />
            <stop
              offset={`${gradientOffsets.warning}%`}
              stopColor={theme.palette.warning.main}
            />
            <stop
              offset={`${gradientOffsets.safe}%`}
              stopColor={theme.palette.primary.main}
            />
            <stop offset="100%" stopColor={theme.palette.primary.light} />
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
            showMark: true,
          },
          {
            id: "budget-limit",
            dataKey: "allocated",
            label: "Budget",
            color: theme.palette.text.disabled,
            curve: "step",
            strokeDashArray: "8 4",
            showMark: false,
          },
        ]}
        sx={{
          "& .MuiAreaElement-series-spending-series": {
            fillOpacity: 0.2,
          },
          "& .MuiLineElement-series-spending-series": {
            strokeWidth: 3,
          },
          "& .MuiChartsGrid-line": {
            stroke: alpha(theme.palette.divider, 0.1),
          },
        }}
      />
    </Box>
  );
};

export default MonthlyLineChart;
