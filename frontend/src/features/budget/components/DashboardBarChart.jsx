import { BarChart } from "@mui/x-charts/BarChart";
import { useTheme } from "@mui/material/styles";
import { Box, Stack, useMediaQuery } from "@mui/material";

import { useChartPagination } from "../../../hooks/useChartPagination";
import { CATEGORIES } from "../../../utils/constants";
import ChartControls from "../../../components/common/ChartControls";

const DashboardBarChart = ({ data }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const transformedData = CATEGORIES.map((cat) => {
    const rawData = data?.[0] || {};
    return {
      category: cat,
      spent: parseFloat(rawData[cat] || 0),
      allocated: 250,
    };
  });

  const { page, totalPages, currentData, handleNext, handlePrev, setIsPaused } =
    useChartPagination(transformedData);

  return (
    <Stack
      direction="column"
      justifyContent="space-between"
      alignItems="stretch"
      sx={{ mb: 2, px: 1, width: "100%", height: "100%" }}
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
                fontSize: isMobile ? 9 : 11,
                fill: theme.palette.text.secondary,
                fontWeight: 600,
              },
            },
          ]}
          xAxis={[
            {
              tickNumber: isMobile ? 3 : 5,
              valueFormatter: (value) => `$${value.toLocaleString()}`,
              tickLabelStyle: {
                fontSize: 10,
                fill: theme.palette.text.secondary,
              },
            },
          ]}
          series={[
            {
              dataKey: "spent",
              label: "Actual Spent",
              valueFormatter: (v) => `$${v?.toLocaleString()}`,
              color: theme.palette.primary.main,
            },
            {
              dataKey: "allocated",
              label: "Budgeted",
              valueFormatter: (v) => `$${v?.toLocaleString()}`,
              color: theme.palette.grey[200],
            },
          ]}
          height={350}
          margin={{
            left: isMobile ? 10 : 20,
            right: isMobile ? 10 : 20,
            top: 40,
            bottom: 10,
          }}
          slotProps={{
            legend: {
              direction: "row",
              position: { vertical: "top", horizontal: "middle" },
              padding: { bottom: 20 },
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
