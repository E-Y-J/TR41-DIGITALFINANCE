import {
  Card,
  CardContent,
  Box,
  Typography,
  LinearProgress,
  IconButton,
  Tooltip,
  Chip,
  alpha,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { getCategoryColor } from "../../../utils/constants";

const BudgetCard = ({ budget, onEdit, onDelete }) => {
  const {
    budget_type,
    category_name,
    amount,
    spent,
    remaining,
    percentage_used,
    is_warning,
    is_exceeded,
    period,
  } = budget;

  const isTotal = budget_type === "total";
  const displayName = isTotal ? "Total Budget" : category_name;
  const color = isTotal ? "#5C6BC0" : getCategoryColor(category_name);

  const progressColor = is_exceeded
    ? "error"
    : is_warning
      ? "warning"
      : "primary";

  const formatCurrency = (val) => {
    const num = parseFloat(val) || 0;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(num);
  };

  return (
    <Card
      sx={{
        borderRadius: 3,
        border: "1px solid",
        borderColor: is_exceeded
          ? "error.light"
          : is_warning
            ? "warning.light"
            : "grey.200",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
        transition: "all 0.2s ease",
        "&:hover": {
          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          transform: "translateY(-2px)",
        },
      }}
    >
      <CardContent sx={{ p: 2.5, pb: "16px !important" }}>
        {/* Header */}
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            mb: 2,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                bgcolor: alpha(color, 0.15),
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isTotal ? (
                <TrendingUpIcon sx={{ color, fontSize: 22 }} />
              ) : (
                <Typography
                  sx={{
                    fontWeight: 700,
                    color,
                    fontSize: 16,
                  }}
                >
                  {category_name?.charAt(0) || "?"}
                </Typography>
              )}
            </Box>
            <Box>
              <Typography fontWeight={600} variant="body1">
                {displayName}
              </Typography>
              <Chip
                label={period === "weekly" ? "Weekly" : "Monthly"}
                size="small"
                sx={{
                  height: 20,
                  fontSize: "0.7rem",
                  bgcolor: "grey.100",
                  mt: 0.5,
                }}
              />
            </Box>
          </Box>

          <Box sx={{ display: "flex", gap: 0.5 }}>
            {(is_warning || is_exceeded) && (
              <Tooltip title={is_exceeded ? "Budget exceeded!" : "Near limit"}>
                <WarningAmberIcon
                  sx={{
                    color: is_exceeded ? "error.main" : "warning.main",
                    fontSize: 20,
                  }}
                />
              </Tooltip>
            )}
            <Tooltip title="Edit">
              <IconButton size="small" onClick={() => onEdit(budget)}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                size="small"
                onClick={() => onDelete(budget)}
                sx={{ color: "error.light", "&:hover": { color: "error.main" } }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: 1.5 }}>
          <LinearProgress
            variant="determinate"
            value={Math.min(percentage_used || 0, 100)}
            color={progressColor}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: "grey.100",
              "& .MuiLinearProgress-bar": {
                borderRadius: 4,
              },
            }}
          />
        </Box>

        {/* Stats */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Spent
            </Typography>
            <Typography fontWeight={600} variant="body2">
              {formatCurrency(spent)} / {formatCurrency(amount)}
            </Typography>
          </Box>
          <Box sx={{ textAlign: "right" }}>
            <Typography variant="caption" color="text.secondary">
              Remaining
            </Typography>
            <Typography
              fontWeight={600}
              variant="body2"
              color={
                is_exceeded
                  ? "error.main"
                  : is_warning
                    ? "warning.main"
                    : "success.main"
              }
            >
              {formatCurrency(remaining)}
            </Typography>
          </Box>
          <Box sx={{ textAlign: "right" }}>
            <Typography variant="caption" color="text.secondary">
              Used
            </Typography>
            <Typography fontWeight={700} variant="body2" color={progressColor}>
              {(percentage_used || 0).toFixed(0)}%
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BudgetCard;
