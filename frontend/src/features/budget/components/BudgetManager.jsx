import { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  CircularProgress,
  Chip,
  Alert,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import { useGetBudgets } from "../useGetBudgets";
import BudgetCard from "./BudgetCard";
import BudgetModal from "./BudgetModal";
import DeleteBudgetDialog from "./DeleteBudgetDialog";

const BudgetManager = () => {
  const { data, isLoading, error } = useGetBudgets();
  const budgets = data?.items || [];
  const meta = data?.meta || {};

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState(null);

  const handleCreate = () => {
    setSelectedBudget(null);
    setCreateModalOpen(true);
  };

  const handleEdit = (budget) => {
    setSelectedBudget(budget);
    setEditModalOpen(true);
  };

  const handleDelete = (budget) => {
    setSelectedBudget(budget);
    setDeleteDialogOpen(true);
  };

  const handleCloseModals = () => {
    setCreateModalOpen(false);
    setEditModalOpen(false);
    setDeleteDialogOpen(false);
    setSelectedBudget(null);
  };

  // Separate total and category budgets
  const totalBudgets = budgets.filter((b) => b.budget_type === "total");
  const categoryBudgets = budgets.filter((b) => b.budget_type === "category");

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 4,
        border: "1px solid",
        borderColor: "grey.200",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: 3,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <AccountBalanceWalletIcon color="primary" />
          <Typography variant="h6" fontWeight={700}>
            My Budgets
          </Typography>
          {meta.warning_count > 0 && (
            <Chip
              label={`${meta.warning_count} near limit`}
              color="warning"
              size="small"
              sx={{ fontSize: "0.7rem" }}
            />
          )}
          {meta.exceeded_count > 0 && (
            <Chip
              label={`${meta.exceeded_count} exceeded`}
              color="error"
              size="small"
              sx={{ fontSize: "0.7rem" }}
            />
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
          sx={{ borderRadius: 3 }}
        >
          Add Budget
        </Button>
      </Box>

      {/* Content */}
      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          Failed to load budgets. Please try again.
        </Alert>
      ) : budgets.length === 0 ? (
        <Box
          sx={{
            textAlign: "center",
            py: 6,
            color: "text.secondary",
          }}
        >
          <AccountBalanceWalletIcon
            sx={{ fontSize: 48, mb: 2, opacity: 0.3 }}
          />
          <Typography variant="h6" gutterBottom>
            No budgets yet
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Create your first budget to start tracking your spending limits.
          </Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Create Budget
          </Button>
        </Box>
      ) : (
        <Box>
          {/* Total Budgets */}
          {totalBudgets.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="subtitle2"
                color="text.secondary"
                sx={{ mb: 1.5, textTransform: "uppercase", letterSpacing: 0.5 }}
              >
                Overall Budget
              </Typography>
              <Grid container spacing={2}>
                {totalBudgets.map((budget) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={budget.id}>
                    <BudgetCard
                      budget={budget}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Category Budgets */}
          {categoryBudgets.length > 0 && (
            <Box>
              <Typography
                variant="subtitle2"
                color="text.secondary"
                sx={{ mb: 1.5, textTransform: "uppercase", letterSpacing: 0.5 }}
              >
                Category Budgets
              </Typography>
              <Grid container spacing={2}>
                {categoryBudgets.map((budget) => (
                  <Grid size={{ xs: 12, sm: 6, md: 4 }} key={budget.id}>
                    <BudgetCard
                      budget={budget}
                      onEdit={handleEdit}
                      onDelete={handleDelete}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Box>
      )}

      {/* Modals */}
      <BudgetModal
        open={createModalOpen}
        onClose={handleCloseModals}
        budget={null}
      />

      <BudgetModal
        open={editModalOpen}
        onClose={handleCloseModals}
        budget={selectedBudget}
      />

      <DeleteBudgetDialog
        open={deleteDialogOpen}
        onClose={handleCloseModals}
        budget={selectedBudget}
      />
    </Paper>
  );
};

export default BudgetManager;
