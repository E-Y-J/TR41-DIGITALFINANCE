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
import { useDeleteTransaction } from "../useDeleteTransaction";
import { useState } from "react";

const DeleteTransactionDialog = ({ open, onClose, transaction }) => {
  const theme = useTheme();
  const { mutate, isPending } = useDeleteTransaction();
  const [error, setError] = useState(null);

  const handleConfirm = () => {
    if (!transaction?.id) return;

    mutate(transaction.id, {
      onSuccess: () => {
        onClose();
      },
      onError: (err) => {
        setError(err.response?.data?.message || "Failed to delete transaction");
      },
    });
  };

  const merchantName = transaction?.merchant_name || "this transaction";
  const amount = transaction?.amount
    ? `$${parseFloat(transaction.amount).toFixed(2)}`
    : "";

  return (
    <Dialog
      open={open}
      onClose={isPending ? null : onClose}
      maxWidth="xs"
      fullWidth
      slotProps={{
        paper: {
          sx: {
            borderRadius: 4,
            p: 1,
          },
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
        Delete Transaction
      </DialogTitle>
      <DialogContent>
        <Typography color="text.secondary">
          Are you sure you want to delete{" "}
          <strong>
            {amount} at {merchantName}
          </strong>
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
        <Button
          onClick={onClose}
          disabled={isPending}
          sx={{ borderRadius: 2, textTransform: "none" }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          color="error"
          disabled={isPending}
          sx={{ borderRadius: 2, textTransform: "none", fontWeight: 600 }}
        >
          {isPending ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            "Delete"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteTransactionDialog;
