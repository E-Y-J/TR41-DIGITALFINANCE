import { useState, useMemo } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  MenuItem,
  Typography,
  IconButton,
  alpha,
  useTheme,
  CircularProgress,
  Snackbar,
  keyframes,
  Alert,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useUpdateTransaction } from "../useUpdateTransaction";
import { CATEGORIES, getLocalISODate } from "../../../utils/constants";

const shrink = keyframes`
  from { width: 100%; }
  to { width: 0%; }
`;

export const EditTransactionModal = ({
  open,
  onClose,
  transaction,
  categories = [],
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";
  const todayStr = getLocalISODate(new Date(), "daily");

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const initialForm = useMemo(
    () => ({
      merchant_name: transaction?.merchant_name || "",
      amount: transaction?.amount || "",
      transaction_type: transaction?.transaction_type || "expense",

      category_id: transaction?.category_id || transaction?.category_name || "",
      date: transaction?.date || todayStr,
    }),
    [transaction, todayStr],
  );

  const [form, setForm] = useState(initialForm);

  const transactionId = transaction?.id;
  const [lastTransactionId, setLastTransactionId] = useState(null);

  if (transactionId && transactionId !== lastTransactionId) {
    setLastTransactionId(transactionId);
    setForm(initialForm);
  }

  const { mutate, isPending } = useUpdateTransaction();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") return;
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleSubmit = () => {
    const { merchant_name, amount, date } = form;

    if (!merchant_name || !amount || !date) {
      window.alert("Please fill in Merchant, Amount, and Date.");
      return;
    }

    if (date > todayStr) {
      window.alert("Transaction date cannot be in the future.");
      return;
    }

    mutate(
      { transactionId: transaction.id, data: form },
      {
        onSuccess: (response) => {
          const msg =
            response?.data?.message || "Transaction updated successfully";
          setSnackbar({ open: true, message: msg, severity: "success" });
          onClose();
        },
        onError: (err) => {
          const errorMsg =
            err.response?.data?.message || "Something went wrong.";
          setSnackbar({ open: true, message: errorMsg, severity: "error" });
        },
      },
    );
  };

  const textFieldStyles = {
    flex: 1,
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: isDarkMode
        ? alpha(theme.palette.background.default, 0.5)
        : "action.hover",
      transition: "all 0.2s ease-in-out",
      "&:hover": {
        backgroundColor: "action.selected",
        "& .MuiOutlinedInput-notchedOutline": { borderColor: "divider" },
      },
      "&.Mui-focused": {
        backgroundColor: "background.paper",
        boxShadow: isDarkMode
          ? "0 4px 12px rgba(0,0,0,0.5)"
          : "0 4px 12px rgba(0,0,0,0.05)",
      },
    },
    "& .MuiInputLabel-root": { fontWeight: 500, color: "text.secondary" },
  };

  return (
    <>
      <Dialog
        open={open}
        onClose={isPending ? null : onClose}
        fullWidth
        maxWidth="xs"
        slotProps={{
          paper: {
            sx: {
              borderRadius: 5,
              p: 1,
              boxShadow: isDarkMode
                ? "0 24px 48px rgba(0,0,0,0.6)"
                : "0 24px 48px rgba(0,0,0,0.12)",
              backgroundImage: "none",
            },
          },
          backdrop: {
            sx: {
              backgroundColor: isDarkMode
                ? "rgba(0, 0, 0, 0.7)"
                : "rgba(0, 0, 0, 0.4)",
              backdropFilter: "blur(4px)",
            },
          },
        }}
      >
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            pr: 2,
            pt: 1,
          }}
        >
          <DialogTitle sx={{ fontWeight: 800, fontSize: "1.25rem" }}>
            Edit Transaction
          </DialogTitle>
          <IconButton
            onClick={onClose}
            size="small"
            sx={{ color: "text.secondary" }}
            disabled={isPending}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>

        <DialogContent sx={{ borderTop: "none", pb: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Update the details of this transaction.
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
            <TextField
              label="Merchant Name"
              name="merchant_name"
              fullWidth
              value={form.merchant_name}
              onChange={handleChange}
              sx={textFieldStyles}
              required
              disabled={isPending}
            />

            <Box sx={{ display: "flex", gap: 2 }}>
              <TextField
                label="Amount"
                name="amount"
                type="number"
                fullWidth
                value={form.amount}
                onChange={handleChange}
                sx={textFieldStyles}
                required
                disabled={isPending}
              />
              <TextField
                select
                label="Type"
                name="transaction_type"
                fullWidth
                value={form.transaction_type}
                onChange={handleChange}
                sx={{ ...textFieldStyles, minWidth: "120px" }}
                disabled={isPending}
              >
                <MenuItem value="income">Income</MenuItem>
                <MenuItem value="expense">Expense</MenuItem>
              </TextField>
            </Box>

            <TextField
              select
              label="Category"
              name="category_id"
              fullWidth
              value={form.category_id}
              onChange={handleChange}
              sx={textFieldStyles}
              disabled={isPending}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {categories.length > 0
                ? categories.map((cat) => (
                    <MenuItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </MenuItem>
                  ))
                : CATEGORIES.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
            </TextField>

            <TextField
              label="Date"
              name="date"
              type="date"
              fullWidth
              slotProps={{
                htmlInput: { max: todayStr },
                inputLabel: { shrink: true },
              }}
              value={form.date}
              onChange={handleChange}
              sx={textFieldStyles}
              required
              disabled={isPending}
            />
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button
            onClick={onClose}
            disabled={isPending}
            sx={{
              color: "text.secondary",
              fontWeight: 600,
              textTransform: "none",
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={isPending}
            sx={{
              borderRadius: 2.5,
              textTransform: "none",
              fontWeight: 700,
              minWidth: 140,
              px: 4,
              py: 1,
              boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.25)}`,
            }}
          >
            {isPending ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              "Update Transaction"
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
