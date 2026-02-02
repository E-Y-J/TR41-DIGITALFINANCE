import { LineChart } from "@mui/x-charts/LineChart";
import { useTheme, alpha } from "@mui/material/styles";
import { Box, Typography, Paper } from "@mui/material";
import SentimentDissatisfiedIcon from "@mui/icons-material/SentimentDissatisfied";

const NoDataView = () => (
  <Paper
    variant="outlined"
    sx={{
      height: 500,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      bgcolor: (theme) => alpha(theme.palette.action.hover, 0.5),
      borderStyle: "dashed",
      borderColor: "divider",
    }}
  >
    <SentimentDissatisfiedIcon
      sx={{ fontSize: 48, color: "text.secondary", mb: 2 }}
    />
    <Typography color="text.primary" fontWeight={600}>
      No spending data found
    </Typography>
    <Typography variant="caption" color="text.secondary">
      Try selecting a different month or category.
    </Typography>
  </Paper>
);

const DailySpendingChart = ({ data, isLoading }) => {
  const theme = useTheme();

  if (!isLoading && (!data || data.length === 0)) {
    return <NoDataView />;
  }

  const chartMargin = { top: 20, right: 30, bottom: 80, left: 70 };

  return (
    <Box sx={{ width: "100%", height: 500 }}>
      <svg width={0} height={0}>
        <defs>
          <linearGradient id="spentGradient" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="0%"
              stopColor={theme.palette.primary.main}
              stopOpacity={0.3}
            />
            <stop
              offset="100%"
              stopColor={theme.palette.primary.main}
              stopOpacity={0.0}
            />
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
            label: "Date",
            tickLabelStyle: {
              fontSize: 10,
              angle: -45,
              textAnchor: "end",
              fill: theme.palette.text.secondary,
            },
          },
        ]}
        yAxis={[
          {
            label: "Amount ($)",
            valueFormatter: (value) => `$${value}`,
            tickLabelStyle: {
              fontSize: 12,
              fill: theme.palette.text.secondary,
            },
          },
        ]}
        series={[
          {
            dataKey: "spent",
            label: "Spent",
            color: theme.palette.primary.main,
            showMark: false,
            curve: "natural",

            area: true,
            connectNulls: true,
            disableHighlight: false,
          },
          {
            dataKey: "allocated",
            label: "Allocated",
            color: theme.palette.grey[400],
            showMark: false,
            curve: "step",
            lineStyle: {
              strokeDasharray: "8 4",
              strokeWidth: 2,
            },
            disableHighlight: true,
          },
        ]}
        sx={{
          "& .MuiAreaElement-root": {
            fill: "url(#spentGradient)",
          },
        }}
        slotProps={{
          legend: {
            hidden: false,
            position: { vertical: "top", horizontal: "right" },
            padding: 0,
            itemMarkWidth: 10,
            itemMarkHeight: 10,
          },
        }}
      />
    </Box>
  );
};

export default DailySpendingChart;
