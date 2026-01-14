import { BarChart } from "@mui/x-charts/BarChart";
import { useTheme } from "@mui/material/styles";

const dataset = [
  { category: "Food", spent: 450, allocated: 600 },
  { category: "Bills", spent: 980, allocated: 1000 },
  { category: "Auto", spent: 320, allocated: 250 },
  { category: "Education", spent: 150, allocated: 200 },
  { category: "Shopping", spent: 410, allocated: 300 },
  { category: "Entertainment", spent: 120, allocated: 150 },
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
