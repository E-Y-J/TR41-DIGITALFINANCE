import {
  ListItem,
  Box,
  LinearProgress,
  IconButton,
  Typography,
  Stack,
  alpha,
  useTheme,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { getIcon } from "../../../utils/transactionUtils";

const BudgetRow = ({ budget, onEdit, onDelete }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  const percent = Math.min((budget.spent / budget.amount) * 100, 100);

  const isCritical = percent >= 80;
  const isWarning = percent >= 50 && percent < 80;

  const stateColorKey = isCritical
    ? "error"
    : isWarning
      ? "warning"
      : "primary";
  const stateColorValue = theme.palette[stateColorKey].main;

  return (
    <ListItem
      sx={{
        py: { xs: 2, sm: 1.5 },
        px: { xs: 2, sm: 3 },
        "&:hover": { bgcolor: "action.hover" },
      }}
    >
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={{ xs: 2, sm: 0 }}
        alignItems={{ xs: "stretch", sm: "center" }}
        sx={{ width: "100%" }}
      >
        <Stack
          direction="row"
          spacing={2}
          alignItems="center"
          sx={{ minWidth: { sm: "240px" }, flexShrink: 0 }}
        >
          <Box
            sx={{
              p: 1.2,
              borderRadius: "12px",
              bgcolor: alpha(stateColorValue, isDarkMode ? 0.15 : 0.1),
              color: stateColorValue,
              display: "flex",
              flexShrink: 0,
              transition: "all 0.3s ease",
            }}
          >
            {getIcon(
              budget.budget_type === "total"
                ? `${budget.period} total`
                : budget.category_name,
            )}
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="body2" fontWeight={700} color="text.primary">
              {budget.category_name}
            </Typography>
            <Typography
              variant="caption"
              color={`${stateColorKey}.main`}
              fontWeight={600}
            >
              {Math.round(percent)}% used
            </Typography>
          </Box>
        </Stack>

        <Box sx={{ flexGrow: 1, mx: { xs: 0, sm: 4 }, width: "100%" }}>
          <LinearProgress
            variant="determinate"
            value={percent}
            color={stateColorKey}
            sx={{
              height: 6,
              borderRadius: 4,
              bgcolor: alpha(theme.palette.text.primary, 0.05),
              "& .MuiLinearProgress-bar": {
                borderRadius: 4,
              },
            }}
          />
        </Box>

        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ flexShrink: 0 }}
        >
          <Box
            sx={{
              textAlign: { xs: "left", sm: "right" },
              mr: { sm: 3 },
              minWidth: { sm: "110px" },
            }}
          >
            <Typography variant="body2" fontWeight={800} color="text.primary">
              ${budget.spent.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              of ${budget.amount.toLocaleString()}
            </Typography>
          </Box>
          <Stack direction="row" spacing={0.5}>
            <IconButton size="small" onClick={() => onEdit(budget)}>
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              color="error"
              onClick={() => onDelete(budget)}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Stack>
        </Stack>
      </Stack>
    </ListItem>
  );
};

export default BudgetRow;
