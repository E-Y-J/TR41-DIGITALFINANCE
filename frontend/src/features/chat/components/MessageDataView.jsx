import { Box, Typography, Divider } from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import LightbulbIcon from "@mui/icons-material/Lightbulb";

export const SpendingSummary = ({ data }) => (
  <Box sx={{ mt: 1.5, width: "100%" }}>
    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
      Category Breakdown ({data.start_date} - {data.end_date})
    </Typography>
    {data.category_breakdown.map((cat) => (
      <Box key={cat.category_id} sx={{ mb: 1 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
          <Typography variant="caption" sx={{ fontWeight: 600 }}>
            {cat.name}
          </Typography>
          <Typography variant="caption">
            ${cat.amount.toLocaleString()}
          </Typography>
        </Box>
        <Box
          sx={{
            height: 6,
            bgcolor: "grey.100",
            borderRadius: 3,
            overflow: "hidden",
          }}
        >
          <Box
            sx={{
              width: `${cat.percentage}%`,
              height: "100%",
              bgcolor: "primary.main",
            }}
          />
        </Box>
      </Box>
    ))}
    <Divider sx={{ my: 1.5 }} />
    <Box sx={{ display: "flex", justifyContent: "space-between" }}>
      <Typography variant="body2" color="success.main" fontWeight={700}>
        Income: ${data.total_income}
      </Typography>
      <Typography variant="body2" color="error.main" fontWeight={700}>
        Spent: ${data.total_expense}
      </Typography>
    </Box>
  </Box>
);

export const InsightCard = ({ data }) => (
  <Box sx={{ mt: 1.5 }}>
    <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
      <TrendingUpIcon color="warning" />
      <Typography variant="subtitle2" fontWeight={700}>
        Trend: {data.spending_trend.toUpperCase()}
      </Typography>
    </Box>
    <Typography
      variant="caption"
      color="text.secondary"
      sx={{ display: "block", mb: 1 }}
    >
      TIPS & RECOMMENDATIONS
    </Typography>
    {data.recommendations.map((rec, i) => (
      <Paper
        key={i}
        variant="outlined"
        sx={{
          p: 1,
          mb: 1,
          bgcolor: "rgba(255, 167, 38, 0.05)",
          borderColor: "warning.light",
        }}
      >
        <Box sx={{ display: "flex", gap: 1 }}>
          <LightbulbIcon sx={{ fontSize: 16, mt: 0.3 }} color="warning" />
          <Typography variant="caption" fontWeight={500}>
            {rec}
          </Typography>
        </Box>
      </Paper>
    ))}
  </Box>
);
