import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme } from "@mui/material/styles";
import { Box, useMediaQuery, alpha } from "@mui/material";

// need to come back bc of the color styling
const MonthlyLineChart = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  // this is mock for now
  const budgetLimit = 1500;

  const maxDataPoint =
    Math.max(...(data?.map((d) => d.spent) || [0]), budgetLimit) * 1.25;

  const budgetPos = (1 - budgetLimit / maxDataPoint) * 100;
  const warningPos = (1 - (budgetLimit * 0.85) / maxDataPoint) * 100;
  const safePos = (1 - (budgetLimit * 0.5) / maxDataPoint) * 100;

  return (
    <Box sx={{ width: "100%", height: isMobile ? 350 : 500 }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <defs>
          <linearGradient id="financeTrendGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#e53e3e" />
            <stop offset={`${budgetPos}%`} stopColor="#ed8936" />
            <stop offset={`${warningPos}%`} stopColor="#ecc94b" />
            <stop offset={`${safePos}%`} stopColor="#3182ce" />
            <stop offset="100%" stopColor="#f7fafc" />
          </linearGradient>
        </defs>
      </svg>

      <LineChart
        dataset={data}
        margin={{
          top: 40,
          right: isMobile ? 20 : 40,
          bottom: 60,
          left: isMobile ? 40 : 80,
        }}
        xAxis={[
          {
            scaleType: "point",
            dataKey: "month",
            valueFormatter: (value) => {
              if (isMobile) {
                const [month, year] = value.split(" ");
                return `${month} '${year.slice(-2)}`;
              }
              return value;
            },
          },
        ]}
        yAxis={[
          {
            label: isMobile ? "" : "Total Spent ($)",
            min: 0,
            max: maxDataPoint,
            valueFormatter: (val) => `$${val.toLocaleString()}`,
          },
        ]}
        series={[
          {
            id: "spending-series",
            dataKey: "spent",
            label: "Actual Spending",
            area: true,
            curve: "monotoneX",
            color: "url(#financeTrendGradient)",
            showMark: true,
            disableHighlight: true,
            highlightScope: { faded: "none", highlighted: "none" },
          },
          {
            id: "budget-limit",
            dataKey: "allocated",
            label: "Budget Limit",
            color: theme.palette.text.disabled,
            curve: "stepAfter",
            strokeDashArray: "10 6",
            showMark: false,
          },
        ]}
        sx={{
          "& .MuiAreaElement-series-spending-series": {
            fill: "url(#financeTrendGradient)",
            fillOpacity: 0.25,
          },
          "& .MuiLineElement-series-spending-series": {
            strokeWidth: 3,
          },
          "& .MuiMarkElement-root": {
            fill: "#000000 !important",
            stroke: "#ffffff !important",
            strokeWidth: 2,
            r: isMobile ? 4 : 5,
          },
          "& .MuiMarkElement-highlighted, & .MuiMarkElement-faded": {
            fill: "#000000 !important",
            stroke: "#ffffff !important",
            r: isMobile ? 4 : 5,
            opacity: "1 !important",
          },
          "& .MuiChartsGrid-line": {
            strokeDasharray: "4 4",
            stroke: alpha(theme.palette.divider, 0.2),
          },
        }}
      />
    </Box>
  );
};

export default MonthlyLineChart;
