import React, { useState } from "react";
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
  Grid,
  alpha,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

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
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

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

  const handleFormSubmit = (formData) => {
    const mutation = formMode === "create" ? createMutation : updateMutation;
    const params =
      formMode === "create"
        ? formData
        : { loanId: selectedLoan.id, data: formData };

    mutation.mutate(params, {
      onSuccess: (res) => {
        setSnackbar({
          open: true,
          message: res?.data?.message || `Loan ${formMode}d successfully`,
          severity: "success",
        });
        handleCloseModal();
      },
      onError: (err) => {
        setSnackbar({
          open: true,
          message: err.response?.data?.message || "Operation failed",
          severity: "error",
        });
      },
    });
  };

  const handleDeleteConfirm = () => {
    if (!selectedLoan?.id) return;
    deleteMutation.mutate(selectedLoan.id, {
      onSuccess: (res) => {
        setSnackbar({
          open: true,
          message: res?.data?.message || "Deleted",
          severity: "success",
        });
        handleCloseDelete();
      },
      onError: (err) => {
        setSnackbar({
          open: true,
          message: err.response?.data?.message || "Error",
          severity: "error",
        });
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
      maximumFractionDigits: 0,
    }).format(Math.abs(parseFloat(amount) || 0));
  };

  if (isLoading)
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "50vh",
        }}
      >
        <CircularProgress size={40} />
      </Box>
    );

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1200, mx: "auto" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "stretch", md: "flex-end" },
          gap: { xs: 1.5, md: 2 },
          mb: { xs: 3, md: 4 },
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Box sx={{ pb: 1.5 }}>
          <Typography
            variant={isMobile ? "h5" : "h4"}
            fontWeight={900}
            sx={{ letterSpacing: "-0.5px", color: "text.primary" }}
          >
            Loans
          </Typography>
          <Typography variant="caption" color="text.secondary" fontWeight={500}>
            Track your borrowings and repayment progress.
          </Typography>
        </Box>

        <Tabs
          value={status}
          onChange={(e, v) => {
            setStatus(v);
            setPage(1);
          }}
          variant={isMobile ? "fullWidth" : "standard"}
          sx={{
            "& .MuiTab-root": {
              textTransform: "none",
              fontWeight: 600,
              fontSize: { xs: "0.8rem", md: "0.875rem" },
            },
          }}
        >
          <Tab value="all" label="All" />
          <Tab value="open" label="Active" />
          <Tab value="closed" label="Closed" />
        </Tabs>

        <Button
          variant="contained"
          fullWidth={isMobile}
          startIcon={<AddIcon />}
          onClick={handleOpenCreate}
          sx={{
            mb: 1.5,
            borderRadius: 2.5,
            textTransform: "none",
            fontWeight: 800,
            py: { xs: 1.2, md: 1 },
          }}
        >
          Add Loan
        </Button>
      </Box>

      {loans.length === 0 ? (
        <EmptyState
          header="No loans found"
          text="Start by adding your first loan."
        />
      ) : (
        <Stack spacing={1.5}>
          {loans.map((loan) => (
            <Card
              key={loan.id}
              elevation={0}
              sx={{
                borderRadius: 3,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: isDarkMode
                  ? alpha(theme.palette.background.paper, 0.4)
                  : "background.paper",
                transition: "0.2s",
                "&:hover": { borderColor: "primary.main" },
              }}
            >
              <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1.5,
                  }}
                >
                  <Box sx={{ minWidth: 0, flex: 1 }}>
                    <Typography
                      variant="subtitle2"
                      fontWeight={800}
                      noWrap
                      sx={{ lineHeight: 1.2 }}
                    >
                      {loan.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        fontSize: "0.65rem",
                        fontWeight: 700,
                        color: "text.secondary",
                        textTransform: "uppercase",
                        letterSpacing: 0.5,
                        display: "block",
                      }}
                    >
                      {loan.category_name || "General"}
                    </Typography>
                  </Box>

                  <Stack direction="row" spacing={0.5} alignItems="center">
                    {!isMobile && (
                      <Chip
                        label={loan.status === "open" ? "Active" : "Closed"}
                        size="small"
                        color={loan.status === "open" ? "success" : "default"}
                        variant={isDarkMode ? "outlined" : "filled"}
                        sx={{
                          height: 18,
                          fontSize: "0.6rem",
                          fontWeight: 900,
                          borderRadius: 1,
                          mr: 0.5,
                        }}
                      />
                    )}
                    <Tooltip title="Edit Loan" arrow>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenEdit(loan)}
                      >
                        <EditIcon sx={{ fontSize: "1rem" }} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Loan" arrow>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleOpenDelete(loan)}
                      >
                        <DeleteIcon sx={{ fontSize: "1rem" }} />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 0.75,
                    }}
                  >
                    <Typography
                      variant="caption"
                      fontWeight={700}
                      sx={{ fontSize: "0.7rem" }}
                    >
                      {loan.progress_percentage?.toFixed(0)}% Repaid
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ fontSize: "0.65rem" }}
                    >
                      {formatCurrency(
                        loan.original_amount - loan.remaining_amount,
                      )}{" "}
                      Paid
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={loan.progress_percentage || 0}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: alpha(
                        getProgressColor(loan.progress_percentage),
                        0.1,
                      ),
                      "& .MuiLinearProgress-bar": {
                        bgcolor: getProgressColor(loan.progress_percentage),
                      },
                    }}
                  />
                </Box>

                <Divider sx={{ mb: 2, borderStyle: "dashed", opacity: 0.5 }} />

                <Grid
                  container
                  spacing={isMobile ? 1 : 3}
                  sx={{
                    mt: 1,
                    justifyContent: { xs: "space-between", md: "flex-end" },
                  }}
                >
                  <Grid item xs={4} md={2.5}>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      fontWeight={800}
                      sx={{
                        fontSize: "0.55rem",
                        display: "block",
                        letterSpacing: 0.5,
                      }}
                    >
                      REMAINING
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight={900}
                      sx={{
                        color: isDarkMode ? "primary.light" : "primary.main",
                        fontSize: { xs: "0.8rem", sm: "0.95rem" },
                      }}
                    >
                      {formatCurrency(loan.remaining_amount)}
                    </Typography>
                  </Grid>

                  <Grid
                    item
                    xs={4}
                    md={2.5}
                    sx={{ textAlign: { xs: "center", md: "left" } }}
                  >
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      fontWeight={800}
                      sx={{
                        fontSize: "0.55rem",
                        display: "block",
                        letterSpacing: 0.5,
                      }}
                    >
                      ORIGINAL
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight={600}
                      sx={{ fontSize: { xs: "0.8rem", sm: "0.95rem" } }}
                    >
                      {formatCurrency(loan.original_amount)}
                    </Typography>
                  </Grid>

                  <Grid item xs={4} md={2.5} sx={{ textAlign: "right" }}>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      fontWeight={800}
                      sx={{
                        fontSize: "0.55rem",
                        display: "block",
                        letterSpacing: 0.5,
                      }}
                    >
                      {isMobile ? "STATUS" : "START DATE"}
                    </Typography>
                    {isMobile ? (
                      <Chip
                        label={loan.status === "open" ? "Active" : "Closed"}
                        size="small"
                        color={loan.status === "open" ? "success" : "default"}
                        sx={{
                          height: 16,
                          fontSize: "0.55rem",
                          fontWeight: 900,
                          borderRadius: 1,
                          mt: 0.25,
                        }}
                      />
                    ) : (
                      <Typography
                        variant="body2"
                        fontWeight={600}
                        sx={{ fontSize: "0.95rem" }}
                      >
                        {loan.start_date
                          ? new Date(loan.start_date).toLocaleDateString(
                              undefined,
                              { month: "short", year: "2-digit" },
                            )
                          : "N/A"}
                      </Typography>
                    )}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}

          <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(e, v) => setPage(v)}
              color="primary"
              shape="rounded"
              size={isMobile ? "small" : "medium"}
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
      >
        <Alert
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LoansPage;
