import { BarChart } from "@mui/x-charts/BarChart";
import { useTheme } from "@mui/material/styles";
import { Box, Stack, useMediaQuery } from "@mui/material";

import { useChartPagination } from "../../../hooks/useChartPagination";
import { generateChartData } from "../../../utils/chartHelpers";

import ChartControls from "../../../components/common/ChartControls";

const fullDataset = generateChartData();

const DashboardBarChart = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const { page, totalPages, currentData, handleNext, handlePrev, setIsPaused } =
    useChartPagination(fullDataset);

  return (
    <Stack
      direction="column"
      justifyContent="space-between"
      alignItems="stretch"
      sx={{ mb: 2, px: 1, width: "100%" }}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <Box sx={{ width: "100%", flexGrow: 1 }}>
        <BarChart
          dataset={currentData}
          layout="horizontal"
          grid={{ vertical: true }}
          borderRadius={3}
          yAxis={[
            {
              scaleType: "band",
              dataKey: "category",
              categoryGapRatio: 0.3,
              barGapRatio: 0.1,
              tickLabelStyle: {
                fontSize: isMobile ? 10 : 12,
                angle: 0,
                textAnchor: "end",
                fill: theme.palette.text.secondary,
                fontWeight: 500,
              },
            },
          ]}
          xAxis={[
            {
              tickNumber: isMobile ? 3 : 6,

              valueFormatter: (value) => `$${value}`,

              tickLabelStyle: {
                fontSize: isMobile ? 10 : 12,
                fill: theme.palette.text.secondary,
              },

              labelStyle: {
                fontSize: isMobile ? 12 : 14,
                transform: `translateY(${isMobile ? 5 : 0}px)`,
              },
            },
          ]}
          series={[
            {
              dataKey: "spent",
              label: "Spent",
              valueFormatter: (v) => `$${v}`,
              color: theme.palette.primary.main,
              borderRadius: 4,
            },
            {
              dataKey: "allocated",
              label: "Allocated",
              valueFormatter: (v) => `$${v}`,
              color: theme.palette.grey[300],
              borderRadius: 4,
            },
          ]}
          height={350}
          margin={{
            left: isMobile ? 10 : 20,
            right: isMobile ? 10 : 20,
            top: 20,
            bottom: 20,
          }}
          slotProps={{
            legend: {
              hidden: false,
              position: { vertical: "top", horizontal: "middle" },
              padding: 0,
            },
          }}
        />
      </Box>

      <ChartControls
        page={page}
        totalPages={totalPages}
        onNext={handleNext}
        onPrev={handlePrev}
      />
    </Stack>
  );
};

export default DashboardBarChart;
