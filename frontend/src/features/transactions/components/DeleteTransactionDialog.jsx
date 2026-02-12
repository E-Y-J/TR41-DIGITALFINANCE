import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  CircularProgress,
  Box,
  Snackbar,
  Alert,
  keyframes,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { useDeleteTransaction } from "../useDeleteTransaction";
import { useState } from "react";
import { useFormatting } from "../../../hooks/useFormatting";

const shrink = keyframes`
  from { width: 100%; }
  to { width: 0%; }
`;

const DeleteTransactionDialog = ({ open, onClose, transaction }) => {
  const { mutate, isPending } = useDeleteTransaction();
  const { formatCurrency } = useFormatting();

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") return;
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleConfirm = () => {
    if (!transaction?.id) return;

    mutate(transaction.id, {
      onSuccess: (response) => {
        const msg =
          response?.data?.message || "Transaction deleted successfully";
        setSnackbar({ open: true, message: msg, severity: "success" });
        onClose();
      },
      onError: (err) => {
        const errorMsg =
          err.response?.data?.message || "Failed to delete transaction";
        setSnackbar({ open: true, message: errorMsg, severity: "error" });
      },
    });
  };

  const merchantName = transaction?.merchant_name || "this transaction";
  const amount = transaction?.amount ? formatCurrency(transaction.amount) : "";

  return (
    <>
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={1500}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Box
          sx={{
            width: "100%",
            position: "relative",
            overflow: "hidden",
            borderRadius: 2,
          }}
        >
          <Alert
            onClose={handleSnackbarClose}
            severity={snackbar.severity}
            variant="filled"
            sx={{ width: "100%" }}
          >
            {snackbar.message}
          </Alert>
          {snackbar.open && (
            <Box
              sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                height: 4,
                backgroundColor: "rgba(255, 255, 255, 0.7)",
                animation: `${shrink} 1500ms linear forwards`,
              }}
            />
          )}
        </Box>
      </Snackbar>
    </>
  );
};

export default DeleteTransactionDialog;
