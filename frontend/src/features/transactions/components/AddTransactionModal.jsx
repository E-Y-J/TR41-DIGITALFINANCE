import { useState } from "react";
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
import { useCreateTransaction } from "../useCreateTransaction";

import { CATEGORIES, getLocalISODate } from "../../../utils/constants";

const shrink = keyframes`
  from { width: 100%; }
  to { width: 0%; }
`;

export const AddTransactionModal = ({ open, onClose }) => {
  const theme = useTheme();
  const today = getLocalISODate();

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const initialState = {
    merchant_name: "",
    amount: "",
    transaction_type: "expense",
    category: "",
    date: today,
  };

  const [form, setForm] = useState(initialState);
  const { mutate, isPending } = useCreateTransaction();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setSnackbar((prev) => ({
      ...prev,
      open: false,
    }));
  };

  const handleSubmit = () => {
    const { merchant_name, amount, date } = form;

    if (!merchant_name || !amount || !date) {
      window.alert("Please fill in Merchant, Amount, and Date.");
      return;
    }

    if (date > today) {
      window.alert("Transaction date cannot be in the future.");
      return;
    }

    mutate(form, {
      onSuccess: (response) => {
        const msg =
          response?.data?.message || "Transaction created successfully";

        setSnackbar({
          open: true,
          message: msg,
          severity: "success",
        });

        setForm(initialState);
        onClose();
      },
      onError: (err) => {
        const errorMsg = err.response?.data?.message || "Something went wrong.";
        setSnackbar({
          open: true,
          message: errorMsg,
          severity: "error",
        });
      },
    });
  };
  const textFieldStyles = {
    flex: 1,
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: "grey.50",
      transition: "all 0.2s ease-in-out",
      "&:hover": {
        backgroundColor: "#f9f9f9",
        "& .MuiOutlinedInput-notchedOutline": { borderColor: "grey.400" },
      },
      "&.Mui-focused": {
        backgroundColor: "#fff",
        boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
      },
    },
    "& .MuiInputLabel-root": {
      fontWeight: 500,
      color: "text.secondary",
    },
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
              boxShadow: "0 24px 48px rgba(0,0,0,0.12)",
              backgroundImage: "none",
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
            New Transaction
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
            Enter the details of your recent financial activity below.
          </Typography>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
            <TextField
              label="Merchant Name"
              name="merchant_name"
              placeholder="e.g. Starbucks"
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
              label="Category (Optional)"
              name="category"
              fullWidth
              value={form.category}
              onChange={handleChange}
              sx={textFieldStyles}
              disabled={isPending}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {CATEGORIES.map((cat) => (
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
                htmlInput: { max: today },
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
              "&:hover": {
                boxShadow: `0 6px 16px ${alpha(theme.palette.primary.main, 0.35)}`,
              },
            }}
          >
            {isPending ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              "Save Transaction"
            )}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2500}
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
                animation: `2500ms linear forwards ${shrink}`,
              }}
            />
          )}
        </Box>
      </Snackbar>
    </>
  );
};

export default AddTransactionModal;
