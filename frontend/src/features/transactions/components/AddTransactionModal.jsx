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
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

export const AddTransactionModal = ({ open, onClose }) => {
  const theme = useTheme();
  const [form, setForm] = useState({
    merchant_name: "",
    amount: "",
    transaction_type: "expense",
    date: new Date().toISOString().split("T")[0],
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = () => {
    console.log("Submitting:", form);
    onClose();
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
    <Dialog
      open={open}
      onClose={onClose}
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
            />
            <TextField
              select
              label="Type"
              name="transaction_type"
              fullWidth
              value={form.transaction_type}
              onChange={handleChange}
              sx={{ ...textFieldStyles, minWidth: "120px" }}
            >
              <MenuItem value="income">Income</MenuItem>
              <MenuItem value="expense">Expense</MenuItem>
            </TextField>
          </Box>

          <TextField
            label="Date"
            name="date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            value={form.date}
            onChange={handleChange}
            sx={textFieldStyles}
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button
          onClick={onClose}
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
          sx={{
            borderRadius: 2.5,
            textTransform: "none",
            fontWeight: 700,
            px: 4,
            py: 1,
            boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.25)}`,
            "&:hover": {
              boxShadow: `0 6px 16px ${alpha(theme.palette.primary.main, 0.35)}`,
            },
          }}
        >
          Save Transaction
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddTransactionModal;
