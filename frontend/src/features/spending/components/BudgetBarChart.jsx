import { BarChart } from "@mui/x-charts/BarChart";
import { useTheme } from "@mui/material/styles";
import { Box, Stack, useMediaQuery } from "@mui/material";

import { useChartPagination } from "../../../hooks/useChartPagination";
import { generateChartData } from "../../../utils/chartHelpers";

import { ChartControls } from "../../../components/common/ChartControls";

const fullDataset = generateChartData();

const BudgetBarChart = () => {
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
          // ... Axis config ...
          height={350}
          margin={{
            left: isMobile ? 10 : 20,
            right: isMobile ? 10 : 30,
            top: 50,
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

export default BudgetBarChart;
