import { useMemo } from "react";
import { PieChart, pieArcLabelClasses } from "@mui/x-charts/PieChart";
import { useTheme } from "@mui/material/styles";
import { Box, Stack, useMediaQuery } from "@mui/material";

import { useChartPagination } from "../../../hooks/useChartPagination";
import {
  generateChartData,
  transformDataForPie,
  getPieLabelFormatter,
  formatCurrency,
} from "../../../utils/chartHelpers";

import { ChartControls } from "../../../components/common/ChartControls";
import { PieCenterLabel, CustomLegend } from "./PieChartExtras";

const fullDataset = generateChartData();

export default function BudgetBreakdownPie() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const { page, totalPages, currentData, handleNext, handlePrev, setIsPaused } =
    useChartPagination(fullDataset);

  // Transformations
  const chartData = useMemo(
    () => transformDataForPie(currentData),
    [currentData],
  );
  const pageTotal = useMemo(
    () => currentData.reduce((acc, i) => acc + i.allocated, 0),
    [currentData],
  );

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
              data: chartData,
              paddingAngle: 1,
              cornerRadius: 4,
              highlightScope: { fade: "global", highlight: "item" },
              highlighted: { additionalRadius: 10 },
              arcLabelMinAngle: 25,
              valueFormatter: (item) => getPieLabelFormatter(item, isMobile),
            },
          ]}
          margin={{ top: 20, bottom: 20, left: 20, right: 20 }}
          hideLegend
          sx={{
            [`& .${pieArcLabelClasses.root}`]: {
              fill: theme.palette.text.primary,
              fontSize: isMobile ? 10 : 12,
              fontWeight: "bold",
              pointerEvents: "none",
            },
          }}
        >
          <PieCenterLabel primary={formatCurrency(pageTotal)}>
            Page Budget
          </PieCenterLabel>
        </PieChart>
      </Box>

      <CustomLegend data={currentData} />

      <ChartControls
        page={page}
        totalPages={totalPages}
        onNext={handleNext}
        onPrev={handlePrev}
      />
    </Stack>
  );
}
