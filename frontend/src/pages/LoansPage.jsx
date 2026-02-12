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
  Divider,
  Stack,
  LinearProgress,
  Snackbar,
  Alert,
  Tooltip,
  Pagination,
  Tabs,
  Tab,
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
  const isDarkMode = theme.palette.mode === "dark";

  const [status, setStatus] = useState("all");
  const [page, setPage] = useState(1);
  const perPage = 5;

  const { data, isLoading, isError } = useGetLoans({
    status: status === "all" ? "" : status,
    page,
    per_page: perPage,
  });
  const loans = data?.items || [];
  const totalPages = data?.totalPages || 1;

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

  const handleStatusChange = (event, newValue) => {
    setStatus(newValue);
    setPage(1);
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
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1200, mx: "auto" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", md: "flex-end" },
          gap: 2,
          mb: 4,
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Box sx={{ pb: 1.5 }}>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{ letterSpacing: "-0.5px", color: "text.primary" }}
          >
            Loans
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your borrowings and track repayment progress.
          </Typography>
        </Box>

        <Tabs
          value={status}
          onChange={handleStatusChange}
          sx={{
            "& .MuiTab-root": {
              textTransform: "none",
              fontWeight: 600,
              minWidth: 100,
            },
          }}
        >
          <Tab value="all" label="All Loans" />
          <Tab value="open" label="Active" />
          <Tab value="closed" label="Closed" />
        </Tabs>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreate}
          sx={{
            mb: 1,
            borderRadius: 3,
            textTransform: "none",
            fontWeight: 700,
            px: 3,
            py: 1,
            boxShadow: isDarkMode
              ? `0 4px 14px ${alpha(theme.palette.primary.main, 0.4)}`
              : "0 4px 12px rgba(0,0,0,0.15)",
          }}
        >
          Add Loan
        </Button>
      </Box>

      {loans.length === 0 ? (
        <Card
          sx={{
            borderRadius: 4,
            p: 4,
            border: "1px solid",
            borderColor: "divider",
            boxShadow: "none",
          }}
        >
          <EmptyState
            header={status === "all" ? "No loans yet" : `No ${status} loans`}
            text="Start tracking your loans to see your repayment progress here."
          />
        </Card>
      ) : (
        <Stack spacing={2}>
          {loans.map((loan) => (
            <Card
              key={loan.id}
              elevation={0}
              sx={{
                borderRadius: 4,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: isDarkMode
                  ? alpha(theme.palette.background.paper, 0.6)
                  : "background.paper",
                transition: "all 0.25s ease-in-out",
                "&:hover": {
                  borderColor: "primary.main",
                  transform: "translateY(-3px)",
                  boxShadow: isDarkMode
                    ? `0 8px 24px ${alpha(theme.palette.common.black, 0.5)}`
                    : "0 8px 24px rgba(0,0,0,0.04)",
                },
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 2,
                  }}
                >
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      {loan.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: 0.5,
                      }}
                    >
                      {loan.category_name || "General"}
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Chip
                      label={loan.status === "open" ? "Active" : "Closed"}
                      size="small"
                      color={loan.status === "open" ? "success" : "default"}
                      sx={{ fontWeight: 700, borderRadius: 1.5 }}
                    />
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenEdit(loan)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleOpenDelete(loan)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </Box>

                <Box sx={{ mb: 2.5 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2" fontWeight={600}>
                      {loan.progress_percentage?.toFixed(1)}% Repaid
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatCurrency(
                        loan.original_amount - loan.remaining_amount,
                      )}
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
                        0.1,
                      ),
                      "& .MuiLinearProgress-bar": {
                        borderRadius: 4,
                        bgcolor: getProgressColor(loan.progress_percentage),
                      },
                    }}
                  />
                </Box>

                <Divider sx={{ mb: 2, borderStyle: "dashed" }} />

                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={{ xs: 2, md: 6 }}
                  sx={{ mt: 1 }}
                >
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                    >
                      REMAINING
                    </Typography>
                    <Typography
                      variant="body1"
                      fontWeight={700}
                      color="primary.main"
                    >
                      {formatCurrency(loan.remaining_amount)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                    >
                      TOTAL LOAN
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
                      DATE RANGE
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {loan.start_date
                        ? new Date(loan.start_date).toLocaleDateString()
                        : "N/A"}
                      —
                      {loan.end_date
                        ? new Date(loan.end_date).toLocaleDateString()
                        : "Present"}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ))}
          <Box sx={{ mt: 4, display: "flex", justifyContent: "center" }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(e, v) => setPage(v)}
              color="primary"
              shape="rounded"
              size="large"
            />
          </Box>
        </Stack>
      )}

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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
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
