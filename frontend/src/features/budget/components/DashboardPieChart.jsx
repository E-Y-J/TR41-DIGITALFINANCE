import { useMemo } from "react";
import { PieChart } from "@mui/x-charts/PieChart";
import { useTheme } from "@mui/material/styles";
import { Box, Stack, useMediaQuery } from "@mui/material";

import { useChartPagination } from "../../../hooks/useChartPagination";
import {
  transformDataForPie,
  getPieLabelFormatter,
  formatCurrency,
} from "../../../utils/chartHelpers";

import ChartControls from "../../../components/common/ChartControls";
import { PieCenterLabel, CustomLegend } from "./PieChartExtras";

const DashboardPieChart = ({ data }) => {
  const pieData = transformDataForPie(data);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  console.log("DashboardPieChart - pieData:", data);
  const { page, totalPages, currentData, handleNext, handlePrev, setIsPaused } =
    useChartPagination(pieData, 10);

  const combinedTotalSpent = useMemo(() => {
    return pieData
      .filter((item) => item.isSpent)
      .reduce((acc, curr) => acc + curr.fullSpent, 0);
  }, [pieData]);

  return (
    <Stack
      direction="column"
      sx={{ mb: 2, px: 1, width: "100%" }}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <Box
        sx={{
          width: "100%",
          height: 400,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <PieChart
          series={[
            {
              innerRadius: 80,
              outerRadius: isMobile ? 120 : 150,
              data: currentData,
              paddingAngle: 1,
              cornerRadius: 4,
              highlightScope: { fade: "global", highlight: "item" },
              highlighted: { additionalRadius: 10 },
              arcLabelMinAngle: 25,
              valueFormatter: (item) => getPieLabelFormatter(item, isMobile),
            },
          ]}
          hideLegend
        >
          <PieCenterLabel primary={formatCurrency(combinedTotalSpent)}>
            Total Spent
          </PieCenterLabel>
        </PieChart>
      </Box>

      <CustomLegend data={currentData.filter((item) => item.isSpent)} />

      <ChartControls
        page={page}
        totalPages={totalPages}
        onNext={handleNext}
        onPrev={handlePrev}
      />
    </Stack>
  );
};

export default DashboardPieChart;
