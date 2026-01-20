import { PieChart, pieArcLabelClasses } from "@mui/x-charts/PieChart";
import Box from "@mui/material/Box";
import { useDrawingArea } from "@mui/x-charts/hooks";
import { styled, alpha } from "@mui/material/styles";

const dataset = [
  { category: "Food", allocated: 600, spent: 450 },
  { category: "Bills", allocated: 1000, spent: 980 },
  { category: "Auto", allocated: 250, spent: 320 },
  { category: "Education", allocated: 200, spent: 150 },
  { category: "Shop", allocated: 300, spent: 410 },
  { category: "Entertainment", allocated: 150, spent: 120 },
];

const categoryColors = {
  Food: "#FF7043",
  Bills: "#42A5F5",
  Education: "#EF5350",
  Shop: "#66BB6A",
  Auto: "#AB47BC",
  Entertainment: "#FFA726",
};

const formatCurrency = (value) => `$${value.toLocaleString()}`;

const StyledText = styled("text")(({ theme }) => ({
  fill: theme.palette.text.primary,
  textAnchor: "middle",
  dominantBaseline: "central",
  fontWeight: "bold",
}));

function PieCenterLabel({ children, primary }) {
  const { width, height, left, top } = useDrawingArea();
  return (
    <>
      <StyledText
        x={left + width / 2}
        y={top + height / 2 - 10}
        style={{ fontSize: 22 }}
      >
        {primary}
      </StyledText>
      <StyledText
        x={left + width / 2}
        y={top + height / 2 + 15}
        style={{ fontSize: 12, fill: "#666" }}
      >
        {children}
      </StyledText>
    </>
  );
}

export default function BudgetBreakdownPie() {
  const totalAllocated = dataset.reduce((acc, item) => acc + item.allocated, 0);

  const chartData = dataset.flatMap((item) => {
    const color = categoryColors[item.category];

    const safeSpent = Math.min(item.spent, item.allocated);
    const remaining = Math.max(0, item.allocated - item.spent);

    return [
      {
        id: `${item.category}-spent`,
        label: item.category,
        value: safeSpent,
        color: color,

        fullAllocated: item.allocated,
        fullSpent: item.spent,
        isSpent: true,
      },
      {
        id: `${item.category}-left`,
        label: `${item.category}`,
        value: remaining,
        color: alpha(color, 0.45),
        fullAllocated: item.allocated,
        fullSpent: item.spent,
        isSpent: false,
      },
    ];
  });

  return (
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
            outerRadius: 150,
            data: chartData,
            paddingAngle: 0,

            highlightScope: { fade: "global", highlight: "item" },
            highlighted: { additionalRadius: 10 },
            cornerRadius: 4,

            arcLabel: (item) => (item.isSpent ? item.label : ""),
            arcLabelMinAngle: 20,

            valueFormatter: (item) => {
              const percent = Math.round(
                (item.fullSpent / item.fullAllocated) * 100,
              );
              const spentStr = formatCurrency(item.fullSpent);
              const totalStr = formatCurrency(item.fullAllocated);
              const remainingStr = formatCurrency(
                Math.max(0, item.fullAllocated - item.fullSpent),
              );

              if (item.isSpent) {
                return `${spentStr} spent of ${totalStr} (${percent}%)`;
              } else {
                return `${remainingStr} remaining of ${totalStr} (${100 - percent}%)`;
              }
            },
          },
        ]}
        sx={{
          [`& .${pieArcLabelClasses.root}`]: {
            fill: "white",
            fontSize: 12,
            fontWeight: "bold",
            pointerEvents: "none",
          },
        }}
        hideLegend
      >
        <PieCenterLabel primary={formatCurrency(totalAllocated)}>
          Total Budget
        </PieCenterLabel>
      </PieChart>
    </Box>
  );
}
