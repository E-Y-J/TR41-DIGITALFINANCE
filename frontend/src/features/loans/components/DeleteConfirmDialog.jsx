import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  CircularProgress,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

const DeleteConfirmDialog = ({
  open,
  onClose,
  onConfirm,
  isPending,
  loanName,
}) => {
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
        Delete Loan
      </DialogTitle>
      <DialogContent>
        <Typography color="text.secondary">
          Are you sure you want to delete{" "}
          <strong>{loanName || "this loan"}</strong>? This action cannot be
          undone.
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
          onClick={onConfirm}
          variant="contained"
          color="error"
          disabled={isPending}
          sx={{ borderRadius: 2, textTransform: "none", fontWeight: 600 }}
        >
          {isPending ? <CircularProgress size={20} color="inherit" /> : "Delete"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteConfirmDialog;
