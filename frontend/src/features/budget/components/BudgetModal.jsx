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
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  InputAdornment,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useCreateBudget } from "../useCreateBudget";
import { useUpdateBudget } from "../useUpdateBudget";
import { CATEGORIES } from "../../../utils/constants";

const BudgetModal = ({ open, onClose, budget = null, categories = [] }) => {
  const isEdit = Boolean(budget);
  const createMutation = useCreateBudget();
  const updateMutation = useUpdateBudget();
  const isPending = createMutation.isPending || updateMutation.isPending;

  const [form, setForm] = useState({
    budget_type: budget?.budget_type || "category",
    category_id: budget?.category_id || "",
    amount: budget?.amount || "",
    period: budget?.period || "monthly",
    is_active: budget?.is_active ?? true,
  });

  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = () => {
    // Validation
    if (!form.amount || parseFloat(form.amount) <= 0) {
      setError("Please enter a valid budget amount");
      return;
    }

    if (form.budget_type === "category" && !form.category_id) {
      setError("Please select a category");
      return;
    }

    const submitData = {
      budget_type: form.budget_type,
      amount: form.amount.toString(),
      period: form.period,
      is_active: form.is_active,
    };

    if (form.budget_type === "category") {
      submitData.category_id = form.category_id;
    }

    const mutation = isEdit ? updateMutation : createMutation;
    const mutateArgs = isEdit
      ? { budgetId: budget.id, data: submitData }
      : submitData;

    mutation.mutate(mutateArgs, {
      onSuccess: () => {
        onClose();
        setForm({
          budget_type: "category",
          category_id: "",
          amount: "",
          period: "monthly",
          is_active: true,
        });
      },
      onError: (err) => {
        setError(
          err.response?.data?.message ||
            err.response?.data?.error?.message ||
            "Failed to save budget"
        );
      },
    });
  };

  const textFieldStyles = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: "grey.50",
      "&:hover": {
        backgroundColor: "#f9f9f9",
      },
      "&.Mui-focused": {
        backgroundColor: "#fff",
      },
    },
  };

  return (
    <Dialog
      open={open}
      onClose={isPending ? null : onClose}
      fullWidth
      maxWidth="xs"
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
          justifyContent: "space-between",
          fontWeight: 700,
        }}
      >
        {isEdit ? "Edit Budget" : "Create Budget"}
        <IconButton
          onClick={onClose}
          disabled={isPending}
          size="small"
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Budget Type */}
          {!isEdit && (
            <FormControl fullWidth sx={textFieldStyles}>
              <InputLabel>Budget Type</InputLabel>
              <Select
                name="budget_type"
                value={form.budget_type}
                label="Budget Type"
                onChange={handleChange}
              >
                <MenuItem value="total">Total Budget (All Spending)</MenuItem>
                <MenuItem value="category">Category Budget</MenuItem>
              </Select>
            </FormControl>
          )}

          {/* Category Selection (only for category type) */}
          {form.budget_type === "category" && !isEdit && (
            <FormControl fullWidth sx={textFieldStyles}>
              <InputLabel>Category</InputLabel>
              <Select
                name="category_id"
                value={form.category_id}
                label="Category"
                onChange={handleChange}
              >
                {categories.length > 0 ? (
                  categories.map((cat) => (
                    <MenuItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </MenuItem>
                  ))
                ) : (
                  CATEGORIES.filter((c) => c !== "Income").map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          )}

          {/* Show category name for edit mode */}
          {isEdit && budget?.category_name && (
            <TextField
              label="Category"
              value={budget.category_name}
              disabled
              fullWidth
              sx={textFieldStyles}
            />
          )}

          {/* Amount */}
          <TextField
            label="Budget Amount"
            name="amount"
            type="number"
            value={form.amount}
            onChange={handleChange}
            fullWidth
            required
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">$</InputAdornment>
                ),
              },
            }}
            sx={textFieldStyles}
          />

          {/* Period */}
          <FormControl fullWidth sx={textFieldStyles}>
            <InputLabel>Period</InputLabel>
            <Select
              name="period"
              value={form.period}
              label="Period"
              onChange={handleChange}
            >
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="caption" color="text.secondary">
            {form.budget_type === "total"
              ? "Set a limit for your total spending across all categories."
              : "Set a spending limit for a specific category."}
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={isPending}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={isPending}
          sx={{ minWidth: 100 }}
        >
          {isPending ? (
            <CircularProgress size={20} color="inherit" />
          ) : isEdit ? (
            "Save"
          ) : (
            "Create"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BudgetModal;
