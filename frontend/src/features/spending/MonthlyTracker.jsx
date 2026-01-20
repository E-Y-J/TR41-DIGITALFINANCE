import { BarChart } from "@mui/x-charts/BarChart";
import { useTheme } from "@mui/material/styles";

const dataset = [
  { category: "Food", allocated: 600, spent: 450 },
  { category: "Bills", allocated: 1000, spent: 980 },
  { category: "Auto", allocated: 250, spent: 320 },
  { category: "Education", allocated: 200, spent: 150 },
  { category: "Shop", allocated: 300, spent: 410 },
  { category: "Entertainment", allocated: 150, spent: 120 },
];

const valueFormatter = (value) => `$${value}`;

const chartSetting = {
  grid: { vertical: true },
  height: 350,
  margin: 20,
};

export default function BudgetBarChart() {
  const theme = useTheme();
  return (
    <BarChart
      dataset={dataset}
      layout="horizontal"
      yAxis={[
        {
          scaleType: "band",
          dataKey: "category",
          categoryGapRatio: 0.4,
          barGapRatio: 0.1,
        },
      ]}
      xAxis={[{ label: "Amount ($)" }]}
      series={[
        {
          dataKey: "spent",
          label: "Spent",
          valueFormatter,
          color: theme.palette.primary.main,
          borderRadius: 3,
        },
        {
          dataKey: "allocated",
          label: "Allocated",
          valueFormatter,
          color: theme.palette.grey[300],
          borderRadius: 3,
        },
      ]}
      {...chartSetting}
    />
  );
}
