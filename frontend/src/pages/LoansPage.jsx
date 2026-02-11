import { useState } from "react";
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Card,
  CardContent,
  IconButton,
  Chip,
  LinearProgress,
  Snackbar,
  Alert,
  Tooltip,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import { alpha, useTheme } from "@mui/material/styles";

import { useGetLoans } from "../features/loans/useGetLoans";
import {
  useCreateLoan,
  useUpdateLoan,
  useDeleteLoan,
} from "../features/loans/useLoanMutations";
import LoanFormModal from "../features/loans/components/LoanFormModal";
import DeleteConfirmDialog from "../features/loans/components/DeleteConfirmDialog";
import EmptyState from "../components/common/EmptyState";

const LoansPage = () => {
  const theme = useTheme();
  const { data, isLoading, isError } = useGetLoans();
  const loans = data?.items || [];

  const createMutation = useCreateLoan();
  const updateMutation = useUpdateLoan();
  const deleteMutation = useDeleteLoan();

  const [formModalOpen, setFormModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState(null);
  const [formMode, setFormMode] = useState("create");
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const handleOpenCreate = () => {
    setSelectedLoan(null);
    setFormMode("create");
    setFormModalOpen(true);
  };

  const handleOpenEdit = (loan) => {
    setSelectedLoan(loan);
    setFormMode("edit");
    setFormModalOpen(true);
  };

  const handleOpenDelete = (loan) => {
    setSelectedLoan(loan);
    setDeleteDialogOpen(true);
  };

  const handleCloseModal = () => {
    setFormModalOpen(false);
    setSelectedLoan(null);
  };

  const handleCloseDelete = () => {
    setDeleteDialogOpen(false);
    setSelectedLoan(null);
  };

  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleFormSubmit = (data) => {
    if (formMode === "create") {
      createMutation.mutate(data, {
        onSuccess: (response) => {
          const msg = response?.data?.message || "Loan created successfully";
          setSnackbar({ open: true, message: msg, severity: "success" });
          handleCloseModal();
        },
        onError: (err) => {
          const errorMsg =
            err.response?.data?.message || "Failed to create loan";
          setSnackbar({ open: true, message: errorMsg, severity: "error" });
        },
      });
    } else if (selectedLoan?.id) {
      updateMutation.mutate(
        { loanId: selectedLoan.id, data },
        {
          onSuccess: (response) => {
            const msg = response?.data?.message || "Loan updated successfully";
            setSnackbar({ open: true, message: msg, severity: "success" });
            handleCloseModal();
          },
          onError: (err) => {
            const errorMsg =
              err.response?.data?.message || "Failed to update loan";
            setSnackbar({ open: true, message: errorMsg, severity: "error" });
          },
        },
      );
    }
  };

  const handleDeleteConfirm = () => {
    if (!selectedLoan?.id) return;

    deleteMutation.mutate(selectedLoan.id, {
      onSuccess: (response) => {
        const msg = response?.data?.message || "Loan deleted successfully";
        setSnackbar({ open: true, message: msg, severity: "success" });
        handleCloseDelete();
      },
      onError: (err) => {
        const errorMsg = err.response?.data?.message || "Failed to delete loan";
        setSnackbar({ open: true, message: errorMsg, severity: "error" });
      },
    });
  };

  const getProgressColor = (value) => {
    if (value >= 75) return theme.palette.success.main;
    if (value >= 40) return theme.palette.primary.main;
    return theme.palette.warning.main;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "50vh",
        }}
      >
        <CircularProgress size={50} />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error" align="center">
          Failed to load loans. Please try again.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{ letterSpacing: "-0.5px", color: "text.primary" }}
          >
            Loans
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Manage your loans and track your repayment progress.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreate}
          sx={{
            borderRadius: 3,
            textTransform: "none",
            fontWeight: 600,
            px: 3,
            py: 1.5,
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          }}
        >
          Add Loan
        </Button>
      </Box>

      {/* Loans List */}
      {loans.length === 0 ? (
        <Card sx={{ borderRadius: 4, p: 4 }}>
          <EmptyState
            header="No loans yet"
            text="Start tracking your loans by clicking the 'Add Loan' button above."
          />
        </Card>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {loans.map((loan) => (
            <Card
              key={loan.id}
              sx={{
                borderRadius: 4,
                border: "1px solid",
                borderColor: alpha(theme.palette.grey[300], 0.5),
                boxShadow: "none",
                transition: "all 0.3s ease",
                "&:hover": {
                  borderColor: theme.palette.primary.main,
                  transform: "translateY(-2px)",
                  boxShadow: `0 8px 24px ${alpha(theme.palette.common.black, 0.08)}`,
                },
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    mb: 2,
                  }}
                >
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      {loan.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {loan.category_name || "Uncategorized"}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                    <Chip
                      label={loan.status === "open" ? "Active" : "Closed"}
                      size="small"
                      color={loan.status === "open" ? "success" : "default"}
                      sx={{ fontWeight: 600 }}
                    />
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenEdit(loan)}
                        sx={{
                          color: "text.secondary",
                          "&:hover": { color: "primary.main" },
                        }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDelete(loan)}
                        sx={{
                          color: "text.secondary",
                          "&:hover": { color: "error.main" },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Progress: {loan.progress_percentage?.toFixed(1) || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatCurrency(
                        loan.original_amount - loan.remaining_amount,
                      )}{" "}
                      paid
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={loan.progress_percentage || 0}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: alpha(
                        getProgressColor(loan.progress_percentage),
                        0.15,
                      ),
                      "& .MuiLinearProgress-bar": {
                        borderRadius: 4,
                        bgcolor: getProgressColor(loan.progress_percentage),
                      },
                    }}
                  />
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: 2,
                  }}
                >
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                    >
                      Original Amount
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {formatCurrency(loan.original_amount)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                    >
                      Remaining
                    </Typography>
                    <Typography
                      variant="body1"
                      fontWeight={600}
                      color="warning.main"
                    >
                      {formatCurrency(loan.remaining_amount)}
                    </Typography>
                  </Box>
                  {loan.start_date && (
                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        display="block"
                      >
                        Start Date
                      </Typography>
                      <Typography variant="body1">
                        {new Date(loan.start_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  )}
                  {loan.end_date && (
                    <Box>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        display="block"
                      >
                        End Date
                      </Typography>
                      <Typography variant="body1">
                        {new Date(loan.end_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Modals */}
      <LoanFormModal
        open={formModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleFormSubmit}
        isPending={createMutation.isPending || updateMutation.isPending}
        initialData={selectedLoan}
        mode={formMode}
      />

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onClose={handleCloseDelete}
        onConfirm={handleDeleteConfirm}
        isPending={deleteMutation.isPending}
        loanName={selectedLoan?.name}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LoansPage;
