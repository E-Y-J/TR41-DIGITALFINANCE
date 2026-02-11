import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  CircularProgress,
  Box,
  alpha,
  useTheme,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { useDeleteBudget } from "../useDeleteBudget";
import { useState } from "react";

const DeleteBudgetDialog = ({ open, onClose, budget }) => {
  const theme = useTheme();
  const { mutate, isPending } = useDeleteBudget();
  const [error, setError] = useState(null);

  const handleConfirm = () => {
    if (!budget?.id) return;

    mutate(budget.id, {
      onSuccess: () => {
        onClose();
      },
      onError: (err) => {
        setError(err.response?.data?.message || "Failed to delete budget");
      },
    });
  };

  const budgetName =
    budget?.budget_type === "total"
      ? "Total Budget"
      : budget?.category_name || "this budget";

  const formatCurrency = (val) => {
    const num = parseFloat(val) || 0;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(num);
  };

  return (
    <Dialog
      open={open}
      onClose={isPending ? null : onClose}
      maxWidth="xs"
      fullWidth
      slotProps={{
        paper: {
          sx: { borderRadius: 4, p: 1 },
        },
        backdrop: {
          sx: {
            backgroundColor: "rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(4px)",
          },
        },
      }}
    >
      <DialogTitle
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          fontWeight: 700,
          color: "error.main",
        }}
      >
        <WarningAmberIcon />
        Delete Budget
      </DialogTitle>
      <DialogContent>
        <Typography color="text.secondary">
          Are you sure you want to delete the{" "}
          <strong>{budgetName}</strong> budget
          {budget?.amount && (
            <>
              {" "}
              of <strong>{formatCurrency(budget.amount)}</strong>
            </>
          )}
          ? This action cannot be undone.
        </Typography>

        {error && (
          <Box
            sx={{
              mt: 2,
              p: 1.5,
              borderRadius: 2,
              bgcolor: alpha(theme.palette.error.main, 0.1),
              border: `1px solid ${theme.palette.error.light}`,
            }}
          >
            <Typography variant="body2" color="error.main">
              {error}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={isPending}>
          Cancel
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleConfirm}
          disabled={isPending}
          sx={{ minWidth: 80 }}
        >
          {isPending ? <CircularProgress size={20} color="inherit" /> : "Delete"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteBudgetDialog;
