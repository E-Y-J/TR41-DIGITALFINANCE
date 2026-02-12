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
        borderColor: isDarkMode
          ? alpha(mainColor, 0.25)
          : alpha(mainColor, 0.1),
        bgcolor: isDarkMode
          ? alpha(theme.palette.background.paper, 0.5)
          : "background.paper",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        "&:hover": {
          transform: "translateY(-5px)",
          borderColor: mainColor,
          boxShadow: isDarkMode
            ? `0 10px 25px ${alpha(mainColor, 0.25)}`
            : `0 10px 20px ${alpha(mainColor, 0.15)}`,
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
          minHeight: { md: 265 },
        }}
      >
        <Box>
          <Stack
            direction="row"
            spacing={1.75}
            alignItems="center"
            sx={{ mb: 2.5 }}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: "12px",
                flexShrink: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: alpha(mainColor, 0.15),
                color: mainColor,
                boxShadow: isDarkMode
                  ? `inset 0 0 0 1px ${alpha(mainColor, 0.1)}`
                  : "none",
              }}
            >
              {getIcon(isTotal ? `${period} total` : category_name)}
            </Box>

            <Box sx={{ minWidth: 0, flex: 1 }}>
              <Typography
                variant="subtitle1"
                fontWeight={900}
                sx={{
                  color: "text.primary",
                  lineHeight: 1.2,
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                  fontSize: "0.95rem",
                }}
              >
                {displayName}
              </Typography>
            </Box>

            <Stack
              className="action-buttons"
              direction="row"
              spacing={0.5}
              sx={{ opacity: { xs: 1, md: 0 }, transition: "0.2s" }}
            >
              <Tooltip title="Edit Budget" arrow placement="top">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(budget);
                  }}
                >
                  <EditIcon sx={{ fontSize: "1rem" }} />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete Budget" arrow placement="top">
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(budget);
                  }}
                  sx={{ "&:hover": { color: "error.main" } }}
                >
                  <DeleteIcon sx={{ fontSize: "1rem" }} />
                </IconButton>
              </Tooltip>
            </Stack>
          </Stack>

          <Box sx={{ mb: 2, minHeight: 24 }}>
            {is_exceeded && (
              <Chip
                label={`Over by ${formatCurrency(remaining)}`}
                size="small"
                sx={{
                  height: 22,
                  fontSize: "0.7rem",
                  fontWeight: 900,
                  bgcolor: alpha(theme.palette.error.main, 0.15),
                  color: theme.palette.error.light,
                  borderRadius: "6px",
                  border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
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
            sx={{ mb: 1.25 }}
          >
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={800}
                sx={{ mb: 0.25, display: "block" }}
              >
                SPENT
              </Typography>
              <Typography
                variant="h5"
                fontWeight={900}
                sx={{
                  color: is_exceeded ? "error.light" : "text.primary",
                  letterSpacing: "-0.5px",
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
                py: 0.4,
                borderRadius: "6px",
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
              bgcolor: alpha(theme.palette.text.primary, 0.08),
              mb: 2.5,
              "& .MuiLinearProgress-bar": {
                borderRadius: 4,
                bgcolor: mainColor,
                boxShadow: is_exceeded
                  ? `0 0 8px ${alpha(mainColor, 0.4)}`
                  : "none",
              },
            }}
          />

          <Stack
            direction="row"
            justifyContent="space-between"
            sx={{
              pt: 2,
              borderTop: `1px dashed ${alpha(theme.palette.divider, 0.5)}`,
            }}
          >
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={700}
                sx={{ fontSize: "0.65rem" }}
              >
                LIMIT
              </Typography>
              <Typography variant="body2" fontWeight={800} display="block">
                {formatCurrency(amount)}
              </Typography>
            </Box>
            <Box sx={{ textAlign: "right" }}>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={700}
                sx={{ fontSize: "0.65rem" }}
              >
                {is_exceeded ? "DEFICIT" : "REMAINING"}
              </Typography>
              <Typography
                variant="body2"
                fontWeight={800}
                display="block"
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
