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
  const isDarkMode = theme.palette.mode === "dark";

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
        flex: 1,
        width: "100%",
        display: "flex",
        flexDirection: "column",
        minWidth: 0,
        borderRadius: 4,
        backgroundImage: "none",
        border: "1px solid",
        borderColor: isDarkMode ? alpha(mainColor, 0.2) : alpha(mainColor, 0.1),
        bgcolor: isDarkMode
          ? alpha(theme.palette.background.paper, 0.5)
          : "background.paper",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        position: "relative",
        overflow: "hidden",
        "&:hover": {
          transform: "translateY(-6px)",
          borderColor: mainColor,
          boxShadow: isDarkMode
            ? `0 12px 30px ${alpha(mainColor, 0.25)}`
            : `0 12px 24px ${alpha(mainColor, 0.15)}`,
          "& .action-buttons": { opacity: 1 },
        },
      }}
    >
      <CardContent
        sx={{
          p: 2.5,
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          minHeight: { md: 280 },
        }}
      >
        <Box>
          <Stack
            direction="row"
            spacing={1.5}
            alignItems="flex-start"
            sx={{ mb: 2, width: "100%" }}
          >
            <Box
              sx={{
                width: 42,
                height: 42,
                borderRadius: 2.5,
                flexShrink: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: alpha(mainColor, 0.15),
                color: mainColor,
                boxShadow: isDarkMode
                  ? `0 0 10px ${alpha(mainColor, 0.2)}`
                  : "none",
              }}
            >
              {getIcon(isTotal ? `${period} total` : category_name)}
            </Box>

            <Box sx={{ minWidth: 0, flex: 1 }}>
              <Typography
                variant="subtitle2"
                fontWeight={800}
                sx={{
                  color: "text.primary",
                  fontSize: "0.9rem",
                  lineHeight: 1.2,

                  height: "2.4em",
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {displayName}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ fontWeight: 700, opacity: 0.8 }}
              >
                {period?.toUpperCase()}
              </Typography>
            </Box>

            <Stack
              className="action-buttons"
              direction="row"
              spacing={0.5}
              sx={{
                opacity: { xs: 1, md: 0 },
                flexShrink: 0,
                transition: "opacity 0.2s",
              }}
            >
              <Tooltip title="Edit Budget" arrow>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(budget);
                  }}
                  sx={{ bgcolor: isDarkMode ? alpha("#fff", 0.05) : "grey.50" }}
                >
                  <EditIcon sx={{ fontSize: "1rem" }} />
                </IconButton>
              </Tooltip>

              <Tooltip title="Delete Budget" arrow>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(budget);
                  }}
                  sx={{
                    bgcolor: isDarkMode ? alpha("#fff", 0.05) : "grey.50",
                    "&:hover": { color: "error.main" },
                  }}
                >
                  <DeleteIcon sx={{ fontSize: "1rem" }} />
                </IconButton>
              </Tooltip>
            </Stack>
          </Stack>

          <Box sx={{ mb: 2, minHeight: 24 }}>
            {is_exceeded && (
              <Chip
                icon={
                  <ErrorOutlineIcon
                    style={{ fontSize: 14, color: "inherit" }}
                  />
                }
                label={`Over by ${formatCurrency(remaining)}`}
                size="small"
                sx={{
                  fontWeight: 800,
                  bgcolor: alpha(theme.palette.error.main, 0.15),
                  color: theme.palette.error.light,
                  border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                  borderRadius: 1.5,
                }}
              />
            )}
          </Box>
        </Box>

        <Box sx={{ mt: "auto" }}>
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
                fontWeight={800}
              >
                SPENT
              </Typography>
              <Typography
                variant="h6"
                fontWeight={900}
                sx={{
                  color: is_exceeded ? "error.light" : "text.primary",
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
                bgcolor: alpha(mainColor, 0.15),
                px: 1,
                py: 0.3,
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
              height: 10,
              borderRadius: 5,
              bgcolor: isDarkMode
                ? alpha(theme.palette.common.white, 0.08)
                : "grey.100",
              mb: 2.5,
              "& .MuiLinearProgress-bar": {
                borderRadius: 5,
                bgcolor: mainColor,
                boxShadow: is_exceeded
                  ? `0 0 8px ${alpha(mainColor, 0.6)}`
                  : "none",
                backgroundImage: is_exceeded
                  ? `linear-gradient(45deg, ${alpha("#fff", 0.2)} 25%, transparent 25%, transparent 50%, ${alpha("#fff", 0.2)} 50%, ${alpha("#fff", 0.2)} 75%, transparent 75%, transparent)`
                  : "none",
                backgroundSize: "1rem 1rem",
              },
            }}
          />

          <Stack
            direction="row"
            justifyContent="space-between"
            sx={{ pt: 2, borderTop: `1px dashed ${theme.palette.divider}` }}
          >
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ fontWeight: 800, fontSize: "0.65rem" }}
              >
                LIMIT
              </Typography>
              <Typography variant="body2" fontWeight={800}>
                {formatCurrency(amount)}
              </Typography>
            </Box>
            <Box sx={{ textAlign: "right" }}>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ fontWeight: 800, fontSize: "0.65rem" }}
              >
                {is_exceeded ? "DEFICIT" : "REMAINING"}
              </Typography>
              <Typography
                variant="body2"
                fontWeight={800}
                color={is_exceeded ? "error.light" : "success.main"}
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
