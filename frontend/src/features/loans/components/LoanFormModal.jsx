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
  IconButton,
  CircularProgress,
  InputAdornment,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useGetCategories } from "../../categories/useGetCategories";
import { getLocalISODate } from "../../../utils/constants";

const LoanFormContent = ({
  initialData,
  mode,
  onSubmit,
  onClose,
  isPending,
  categories,
  loadingCategories,
}) => {
  const todayStr = getLocalISODate(new Date(), "daily");

  const initialState = useMemo(() => {
    if (mode === "edit" && initialData) {
      return {
        name: initialData.name || "",
        original_amount: initialData.original_amount || "",
        remaining_amount: initialData.remaining_amount || "",
        category_id: initialData.category_id || "",
        start_date: initialData.start_date || "",
        end_date: initialData.end_date || "",
      };
    }
    return {
      name: "",
      original_amount: "",
      remaining_amount: "",
      category_id: "",
      start_date: todayStr,
      end_date: "",
    };
  }, [mode, initialData, todayStr]);

  const [form, setForm] = useState(initialState);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));

    // Auto-fill remaining_amount when original_amount is set in create mode
    if (name === "original_amount" && mode === "create") {
      setForm((prev) => ({ ...prev, remaining_amount: value }));
    }
  };

  const handleSubmit = () => {
    const { name, original_amount, remaining_amount, category_id } = form;

    if (!name || !original_amount || !remaining_amount || !category_id) {
      window.alert(
        "Please fill in Name, Original Amount, Remaining Amount, and Category.",
      );
      return;
    }

    const submitData = {
      name: form.name,
      original_amount: form.original_amount,
      remaining_amount: form.remaining_amount,
      category_id: form.category_id,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
    };

    onSubmit(submitData);
  };

  const textFieldStyles = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: "action.hover",
      transition: "all 0.2s ease-in-out",
      "&:hover": {
        backgroundColor: "action.selected",
        "& .MuiOutlinedInput-notchedOutline": { borderColor: "divider" },
      },
      "&.Mui-focused": {
        backgroundColor: "background.paper",
        boxShadow: (theme) => theme.palette.mode === "dark" ? "0 4px 12px rgba(0,0,0,0.3)" : "0 4px 12px rgba(0,0,0,0.05)",
      },
    },
    "& .MuiInputLabel-root": {
      fontWeight: 500,
      color: "text.secondary",
    },
  };

  return (
    <>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 2,
          pt: 2,
        }}
      >
        <DialogTitle sx={{ p: 0, fontWeight: 700 }}>
          {mode === "create" ? "Add New Loan" : "Edit Loan"}
        </DialogTitle>
        <IconButton
          onClick={onClose}
          disabled={isPending}
          sx={{
            color: "text.secondary",
            "&:hover": { bgcolor: "action.selected" },
          }}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      <DialogContent sx={{ px: 3, py: 2 }}>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
          <TextField
            label="Loan Name"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="e.g., Car Loan, Student Loan"
            fullWidth
            sx={textFieldStyles}
          />

          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Original Amount"
              name="original_amount"
              type="number"
              value={form.original_amount}
              onChange={handleChange}
              placeholder="0.00"
              fullWidth
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">$</InputAdornment>
                  ),
                },
              }}
              sx={textFieldStyles}
            />

            <TextField
              label="Remaining Amount"
              name="remaining_amount"
              type="number"
              value={form.remaining_amount}
              onChange={handleChange}
              placeholder="0.00"
              fullWidth
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">$</InputAdornment>
                  ),
                },
              }}
              sx={textFieldStyles}
            />
          </Box>

          <TextField
            select
            label="Category"
            name="category_id"
            value={form.category_id}
            onChange={handleChange}
            fullWidth
            disabled={loadingCategories}
            sx={textFieldStyles}
          >
            {loadingCategories ? (
              <MenuItem disabled>Loading categories...</MenuItem>
            ) : categories.length === 0 ? (
              <MenuItem disabled>No categories available</MenuItem>
            ) : (
              categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>
                  {cat.name}
                </MenuItem>
              ))
            )}
          </TextField>

          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField
              label="Start Date"
              name="start_date"
              type="date"
              value={form.start_date}
              onChange={handleChange}
              fullWidth
              slotProps={{
                inputLabel: { shrink: true },
              }}
              sx={textFieldStyles}
            />

            <TextField
              label="End Date (Optional)"
              name="end_date"
              type="date"
              value={form.end_date}
              onChange={handleChange}
              fullWidth
              slotProps={{
                inputLabel: { shrink: true },
              }}
              sx={textFieldStyles}
            />
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, pt: 1 }}>
        <Button
          onClick={onClose}
          disabled={isPending}
          sx={{
            borderRadius: 3,
            textTransform: "none",
            fontWeight: 600,
            px: 3,
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isPending}
          sx={{
            borderRadius: 3,
            textTransform: "none",
            fontWeight: 600,
            px: 4,
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            "&:hover": {
              boxShadow: "0 6px 16px rgba(0,0,0,0.2)",
            },
          }}
        >
          {isPending ? (
            <CircularProgress size={20} color="inherit" />
          ) : mode === "create" ? (
            "Add Loan"
          ) : (
            "Save Changes"
          )}
        </Button>
      </DialogActions>
    </>
  );
};

const LoanFormModal = ({
  open,
  onClose,
  onSubmit,
  isPending,
  initialData = null,
  mode = "create",
}) => {
  const { data: categories = [], isLoading: loadingCategories } =
    useGetCategories();

  // Use key to reset form state when modal opens with different data
  const formKey = open ? `${mode}-${initialData?.id || "new"}` : "closed";

  return (
    <Dialog
      open={open}
      onClose={isPending ? null : onClose}
      fullWidth
      maxWidth="sm"
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
      {open && (
        <LoanFormContent
          key={formKey}
          initialData={initialData}
          mode={mode}
          onSubmit={onSubmit}
          onClose={onClose}
          isPending={isPending}
          categories={categories}
          loadingCategories={loadingCategories}
        />
      )}
    </Dialog>
  );
};

export default LoanFormModal;
