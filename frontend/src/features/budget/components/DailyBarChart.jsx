import { Box, Typography, LinearProgress, Stack, Fade } from "@mui/material";
import { CATEGORIES, CATEGORY_COLORS } from "../../../utils/constants";

const DailyBarChart = ({ data, specificCategory }) => {
  const dayData = data[0] || {};
  const totalDailySpend = CATEGORIES.reduce(
    (acc, cat) => acc + (dayData[cat] || 0),
    0,
  );

  const sortedCategories = CATEGORIES.map((cat) => {
    const amount = dayData[cat] || 0;
    return {
      name: cat,
      amount,
      percentage: totalDailySpend > 0 ? (amount / totalDailySpend) * 100 : 0,
      color: CATEGORY_COLORS[cat],
    };
  })
    .sort((a, b) => b.amount - a.amount)
    .filter(
      (item) => specificCategory === "All" || item.name === specificCategory,
    );

  return (
    <Box>
      <Box
        sx={{
          mb: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography variant="subtitle2" color="text.secondary" fontWeight={700}>
          DAILY TOTAL
        </Typography>
        <Typography variant="h5" fontWeight={800} color="primary.main">
          ${totalDailySpend.toLocaleString()}
        </Typography>
      </Box>

      <Stack spacing={1.5}>
        {sortedCategories.map((item, index) => (
          <Fade in timeout={300 + index * 50} key={item.name}>
            <Box sx={{ width: "100%" }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 0.75,
                }}
              >
                <Typography
                  variant="body2"
                  fontWeight={700}
                  sx={{ display: "flex", alignItems: "center", gap: 1 }}
                >
                  {item.name}
                  <Typography
                    component="span"
                    variant="caption"
                    color="text.secondary"
                    fontWeight={500}
                  >
                    ({item.percentage.toFixed(0)}%)
                  </Typography>
                </Typography>
                <Typography
                  variant="body2"
                  fontWeight={800}
                  sx={{ color: item.color }}
                >
                  ${item.amount.toLocaleString()}
                </Typography>
              </Box>

              <LinearProgress
                variant="determinate"
                value={item.percentage}
                sx={{
                  height: 8,
                  borderRadius: 3,
                  bgcolor: "grey.100",
                  "& .MuiLinearProgress-bar": {
                    bgcolor: item.color,
                    borderRadius: 3,
                  },
                }}
              />
            </Box>
          </Fade>
        ))}
      </Stack>
    </Box>
  );
};

export default DailyBarChart;
