import {
  TableRow,
  TableCell,
  Box,
  Typography,
  Avatar,
  Chip,
  alpha,
  useTheme,
} from "@mui/material";

import { getIcon, getStatusLabel } from "../../../utils/transactionUtils";
import { useFormatting } from "../../../hooks/useFormatting";

export const TransactionRow = ({
  row,
  showDate,
  formattedDate,
  onClick,
  isDashboard,
}) => {
  const theme = useTheme();
  const { formatCurrency } = useFormatting();

  const isIncome = row.transaction_type === "income";
  const amountColor = isIncome ? "success.main" : "text.primary";
  const amountPrefix = isIncome ? "+" : "";
  const formattedAmount = `${amountPrefix}${formatCurrency(row.amount)}`;
  const rowStatus = row.status || "completed";

  const getStatusChip = (status = "completed") => {
    const s = status.toLowerCase();
    const label = getStatusLabel(status);

    return (
      <Chip
        label={label}
        size="small"
        variant="outlined"
        sx={{
          height: 24,
          fontSize: "0.75rem",
          fontWeight: 600,
          border: "1px solid",
          borderColor:
            s === "pending"
              ? "warning.light"
              : s === "completed"
                ? "success.light"
                : "error.light",
          bgcolor:
            s === "pending"
              ? alpha(theme.palette.warning.main, 0.05)
              : s === "completed"
                ? alpha(theme.palette.success.main, 0.05)
                : alpha(theme.palette.error.main, 0.05),
          color:
            s === "pending"
              ? "warning.dark"
              : s === "completed"
                ? "success.dark"
                : "error.dark",
          "& .MuiChip-icon": { color: "inherit" },
        }}
      />
    );
  };
  return (
    <TableRow
      hover
      onClick={(event) => onClick(event, row)}
      sx={{
        cursor: "pointer",
        "& td": {
          py: 2,
          borderBottom: "1px solid",
          borderColor: "divider",
        },
        transition: "all 0.2s",
        "&:hover": {
          bgcolor: alpha(theme.palette.primary.main, 0.04),
        },
      }}
    >
      <TableCell
        sx={{
          pl: 3,
          verticalAlign: "top",
          display: { xs: "none", sm: "table-cell" },
        }}
      >
        {showDate && (
          <Typography
            variant="caption"
            fontWeight={700}
            color="text.secondary"
            sx={{
              display: "block",
              mt: 0.5,
              textTransform: "uppercase",
              fontSize: "0.75rem",
              letterSpacing: "0.5px",
            }}
          >
            {formattedDate}
          </Typography>
        )}
      </TableCell>

      <TableCell
        component="th"
        scope="row"
        sx={{
          verticalAlign: "top",
          pl: { xs: 2, sm: 2 },
          width: "auto",
          maxWidth: 0,
          overflow: "hidden",
        }}
      >
        <Box sx={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
          <Box sx={{ display: { xs: "block", sm: "none" }, mb: 1 }}>
            {showDate && (
              <Typography
                variant="caption"
                fontWeight={700}
                color="text.secondary"
                sx={{ textTransform: "uppercase", letterSpacing: "0.5px" }}
              >
                {formattedDate}
              </Typography>
            )}
          </Box>

          <Box
            sx={{ display: "flex", alignItems: "center", gap: 1, minWidth: 0 }}
          >
            <Avatar
              variant="rounded"
              sx={{
                bgcolor: "action.selected",
                color: "primary.main",
                width: 32,
                height: 32,
                borderRadius: 3,
                flexShrink: 0,
              }}
            >
              {getIcon(row.category_name)}
            </Avatar>
            <Box sx={{ minWidth: 0, flex: 1, overflow: "hidden" }}>
              <Typography
                variant="body2"
                fontWeight={600}
                color="text.primary"
                noWrap
                sx={{
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
                  display: "block",
                }}
              >
                {row.merchant_name || "Unknown Merchant"}
              </Typography>
              {row.category_name && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  noWrap
                  sx={{ fontSize: "0.7rem", display: "block" }}
                >
                  {row.category_name}
                </Typography>
              )}
            </Box>
          </Box>
        </Box>
      </TableCell>

      {!isDashboard && (
        <TableCell
          sx={{
            verticalAlign: "middle",
            display: { xs: "none", md: "table-cell" },
          }}
        >
          {getStatusChip(rowStatus, theme)}
        </TableCell>
      )}

      <TableCell
        align="right"
        sx={{
          verticalAlign: "top",
          pr: { xs: 2, sm: 3 },
          width: { xs: "90px", sm: "120px" },
          minWidth: { xs: "90px", sm: "120px" },
        }}
      >
        <Typography
          variant="body2"
          fontWeight={700}
          noWrap
          sx={{
            fontSize: { xs: "0.8rem", sm: "0.875rem" },
            mt: { xs: showDate ? 3.2 : 0.5, sm: 0.5 },
            color: amountColor,
          }}
        >
          {formattedAmount}
        </Typography>
      </TableCell>
    </TableRow>
  );
};
