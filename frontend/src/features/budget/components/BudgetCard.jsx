import React from "react";
import {
  Card,
  CardContent,
  Box,
  Typography,
  LinearProgress,
  IconButton,
  Tooltip,
  Chip,
  Stack,
  alpha,
  useTheme,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { getIcon } from "../../../utils/transactionUtils";

const BudgetCard = ({ budget, onEdit, onDelete }) => {
  const theme = useTheme();
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
  const displayName = isTotal ? "Overall Wallet" : category_name;
  const rawPercent = percentage_used || 0;
  const progressValue = Math.min(rawPercent, 100);

  const statusColor = is_exceeded
    ? "error"
    : is_warning
      ? "warning"
      : "primary";
  const mainColor = theme.palette[statusColor].main;

  const formatCurrency = (val) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(Math.abs(parseFloat(val) || 0));

  return (
    <Card
      sx={{
        height: "100%",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        borderRadius: 4,
        border: "1.5px solid",
        borderColor: alpha(mainColor, 0.1),
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        position: "relative",
        overflow: "visible",
        "&:hover": {
          transform: "translateY(-6px)",
          borderColor: mainColor,
          boxShadow: `0 12px 24px ${alpha(mainColor, 0.15)}`,
          "& .action-buttons": { opacity: 1 },
        },
      }}
    >
      <CardContent
        sx={{ p: 2.5, flexGrow: 1, display: "flex", flexDirection: "column" }}
      >
        {/* Header Section */}
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 2.5 }}
        >
          <Stack
            direction="row"
            spacing={1.5}
            alignItems="center"
            sx={{ minWidth: 0 }}
          >
            <Box
              sx={{
                width: 42,
                height: 42,
                borderRadius: 2.5,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                bgcolor: alpha(mainColor, 0.1),
                color: mainColor,
                boxShadow: `inset 0 0 0 1px ${alpha(mainColor, 0.1)}`,
              }}
            >
              {getIcon(isTotal ? `${period} total` : category_name)}
            </Box>
            <Box sx={{ minWidth: 0 }}>
              <Typography
                variant="subtitle2"
                fontWeight={800}
                noWrap
                sx={{ color: "text.primary", lineHeight: 1.2 }}
              >
                {displayName}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontWeight: 600 }}
              >
                {period?.toUpperCase()}
              </Typography>
            </Box>
          </Stack>

          {/* Improved Spacing for Actions */}
          <Stack
            className="action-buttons"
            direction="row"
            spacing={0.5}
            sx={{
              opacity: { xs: 1, md: 0.6 },
              transition: "opacity 0.2s",
            }}
          >
            <Tooltip title="Edit">
              <IconButton
                size="small"
                onClick={() => onEdit(budget)}
                sx={{
                  bgcolor: "grey.50",
                  "&:hover": {
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                  },
                }}
              >
                <EditIcon sx={{ fontSize: "1.1rem" }} />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                size="small"
                onClick={() => onDelete(budget)}
                sx={{
                  bgcolor: "grey.50",
                  "&:hover": {
                    bgcolor: alpha(theme.palette.error.main, 0.1),
                    color: "error.main",
                  },
                }}
              >
                <DeleteIcon sx={{ fontSize: "1.1rem" }} />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        {/* Status Indicator Area */}
        <Box sx={{ flexGrow: 1, mb: 2 }}>
          {is_exceeded && (
            <Chip
              icon={
                <ErrorOutlineIcon style={{ fontSize: 14, color: "inherit" }} />
              }
              label={`Over by ${formatCurrency(remaining)}`}
              size="small"
              sx={{
                fontWeight: 800,
                bgcolor: alpha(theme.palette.error.main, 0.1),
                color: "error.main",
                border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                borderRadius: 1.5,
                fontSize: "0.65rem",
              }}
            />
          )}
        </Box>

        {/* Progress Section */}
        <Box>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="flex-end"
            sx={{ mb: 1 }}
          >
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={700}
              >
                SPENT
              </Typography>
              <Typography
                variant="h6"
                fontWeight={900}
                sx={{
                  color: is_exceeded ? "error.main" : "text.primary",
                  lineHeight: 1,
                }}
              >
                {formatCurrency(spent)}
              </Typography>
            </Box>
            <Typography
              variant="caption"
              fontWeight={900}
              sx={{
                color: mainColor,
                bgcolor: alpha(mainColor, 0.1),
                px: 1,
                py: 0.2,
                borderRadius: 1,
              }}
            >
              {rawPercent.toFixed(0)}%
            </Typography>
          </Stack>

          <LinearProgress
            variant="determinate"
            value={progressValue}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: "grey.100",
              mb: 2.5,
              "& .MuiLinearProgress-bar": {
                borderRadius: 4,
                bgcolor: mainColor,
                backgroundImage: is_exceeded
                  ? `linear-gradient(45deg, ${alpha("#fff", 0.15)} 25%, transparent 25%, transparent 50%, ${alpha("#fff", 0.15)} 50%, ${alpha("#fff", 0.15)} 75%, transparent 75%, transparent)`
                  : "none",
                backgroundSize: "1rem 1rem",
              },
            }}
          />

          <Stack
            direction="row"
            justifyContent="space-between"
            sx={{
              pt: 2,
              borderTop: `1px dashed ${theme.palette.divider}`,
            }}
          >
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ fontWeight: 700, fontSize: "0.6rem" }}
              >
                LIMIT
              </Typography>
              <Typography variant="body2" fontWeight={800} color="text.primary">
                {formatCurrency(amount)}
              </Typography>
            </Box>
            <Box sx={{ textAlign: "right" }}>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ fontWeight: 700, fontSize: "0.6rem" }}
              >
                {is_exceeded ? "DEFICIT" : "REMAINING"}
              </Typography>
              <Typography
                variant="body2"
                fontWeight={800}
                color={is_exceeded ? "error.main" : "success.main"}
              >
                {formatCurrency(remaining)}
              </Typography>
            </Box>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BudgetCard;
