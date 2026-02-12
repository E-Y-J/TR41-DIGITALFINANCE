import React from "react";
import {
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  LinearProgress,
  IconButton,
  Typography,
  Stack,
  Tooltip,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { getIcon } from "../../../utils/transactionUtils";

const BudgetRow = ({ budget, onEdit, onDelete }) => {
  const percent = Math.min((budget.spent / budget.amount) * 100, 100);
  const isOver = percent >= 100;

  return (
    <ListItem
      sx={{
        py: { xs: 2, sm: 1.5 },
        px: { xs: 2, sm: 3 },
        "&:hover": { bgcolor: "grey.50" },
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
              bgcolor: isOver ? "error.lighter" : "grey.100",
              color: isOver ? "error.main" : "text.secondary",
              display: "flex",
              flexShrink: 0,
            }}
          >
            {getIcon(
              budget.budget_type === "total"
                ? `${budget.period} total`
                : budget.category_name,
            )}
          </Box>
          <Box sx={{ minWidth: 0 }}>
            {" "}
            <Typography
              variant="body2"
              fontWeight={700}
              noWrap
              sx={{ maxWidth: { xs: "180px", sm: "160px" } }}
            >
              {budget.category_name}
            </Typography>
            <Typography
              variant="caption"
              color={isOver ? "error.main" : "text.secondary"}
              fontWeight={600}
            >
              {Math.round(percent)}% used
            </Typography>
          </Box>
        </Stack>

        <Box sx={{ flexGrow: 1, mx: { xs: 0, sm: 4 } }}>
          <LinearProgress
            variant="determinate"
            value={percent}
            color={isOver ? "error" : percent > 80 ? "warning" : "primary"}
            sx={{ height: 6, borderRadius: 4, bgcolor: "grey.100" }}
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
            <Typography variant="body2" fontWeight={800}>
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
