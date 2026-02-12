import React, { useState, useMemo } from "react";
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  CircularProgress,
  Chip,
  Alert,
  Stack,
  IconButton,
  Tooltip,
  Divider,
  List,
  alpha,
  Tabs,
  Tab,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ViewModuleIcon from "@mui/icons-material/ViewModule";
import ViewListIcon from "@mui/icons-material/ViewList";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import { useGetBudgets } from "../useGetBudgets";
import BudgetCard from "./BudgetCard";
import BudgetRow from "./BudgetRow";
import BudgetModal from "./BudgetModal";
import DeleteBudgetDialog from "./DeleteBudgetDialog";

const BudgetManager = () => {
  const { data, isLoading, error } = useGetBudgets();
  const meta = data?.meta || {};

  const [viewMode, setViewMode] = useState("grid");
  const [periodFilter, setPeriodFilter] = useState("monthly");
  const [isExpanded, setIsExpanded] = useState(false);
  const [modalState, setModalState] = useState({ type: null, budget: null });

  const { totalBudgets, categoryBudgets } = useMemo(() => {
    const rawItems = data?.items || [];
    const filteredByPeriod = rawItems.filter((b) => b.period === periodFilter);

    const totals = filteredByPeriod
      .filter((b) => b.budget_type === "total")
      .sort((a, b) => (b.percentage_used || 0) - (a.percentage_used || 0));

    const categories = filteredByPeriod
      .filter((b) => b.budget_type === "category")
      .sort((a, b) => (b.percentage_used || 0) - (a.percentage_used || 0));

    return { totalBudgets: totals, categoryBudgets: categories };
  }, [data, periodFilter]);

  const openModal = (type, budget = null) => setModalState({ type, budget });
  const closeModal = () => setModalState({ type: null, budget: null });

  const visibleCategories = isExpanded
    ? categoryBudgets
    : categoryBudgets.slice(0, 8);

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress size={32} />
      </Box>
    );

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2, md: 3 },
        borderRadius: 4,
        border: "1px solid",
        borderColor: "grey.200",
        bgcolor: "background.paper",
      }}
    >
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={{ xs: 2, sm: 3 }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        sx={{
          mb: 4,
          px: 0.5,
        }}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <AccountBalanceWalletIcon color="primary" sx={{ fontSize: 28 }} />
          <Typography
            variant="h6"
            fontWeight={800}
            sx={{ letterSpacing: -0.5 }}
          >
            My Budgets
          </Typography>

          <Stack direction="row" spacing={1} sx={{ ml: 1 }}>
            {meta.warning_count > 0 && (
              <Tooltip
                title={`${meta.warning_count} budgets are over 80% of their limit`}
              >
                <Chip
                  label={meta.warning_count}
                  color="warning"
                  size="small"
                  variant="outlined"
                  sx={{
                    fontWeight: 800,
                    cursor: "help",
                    height: 24,
                    minWidth: 32,
                    borderRadius: "6px",
                    borderColor: (theme) =>
                      alpha(theme.palette.warning.main, 0.3),
                  }}
                />
              </Tooltip>
            )}
            {meta.exceeded_count > 0 && (
              <Tooltip
                title={`${meta.exceeded_count} budgets have exceeded their limit`}
              >
                <Chip
                  label={meta.exceeded_count}
                  color="error"
                  size="small"
                  sx={{
                    fontWeight: 800,
                    cursor: "help",
                    height: 24,
                    minWidth: 32,
                    borderRadius: "6px",
                  }}
                />
              </Tooltip>
            )}
          </Stack>
        </Stack>

        <Stack
          direction="row"
          spacing={2}
          width={{ xs: "100%", sm: "auto" }}
          alignItems="center"
          justifyContent={{ xs: "space-between", sm: "flex-end" }}
        >
          <Box
            sx={{
              bgcolor: "grey.100",
              p: 0.5,
              borderRadius: "10px",
              display: "flex",
              gap: 0.5,
              border: "1px solid",
              borderColor: "grey.200",
            }}
          >
            <Tooltip title="Grid View">
              <IconButton
                size="small"
                onClick={() => setViewMode("grid")}
                sx={{
                  bgcolor: viewMode === "grid" ? "white" : "transparent",
                  borderRadius: "8px",
                  boxShadow:
                    viewMode === "grid" ? "0 2px 8px rgba(0,0,0,0.08)" : 0,
                  color:
                    viewMode === "grid" ? "primary.main" : "text.secondary",
                  "&:hover": {
                    bgcolor: viewMode === "grid" ? "white" : "grey.200",
                  },
                  transition: "all 0.2s ease",
                }}
              >
                <ViewModuleIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="List View">
              <IconButton
                size="small"
                onClick={() => setViewMode("list")}
                sx={{
                  bgcolor: viewMode === "list" ? "white" : "transparent",
                  borderRadius: "8px",
                  boxShadow:
                    viewMode === "list" ? "0 2px 8px rgba(0,0,0,0.08)" : 0,
                  color:
                    viewMode === "list" ? "primary.main" : "text.secondary",
                  "&:hover": {
                    bgcolor: viewMode === "list" ? "white" : "grey.200",
                  },
                  transition: "all 0.2s ease",
                }}
              >
                <ViewListIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          <Button
            variant="contained"
            disableElevation
            startIcon={<AddIcon />}
            onClick={() => openModal("create")}
            sx={{
              borderRadius: "10px",
              px: 4,
              height: 40,
              textTransform: "none",
              fontWeight: 700,
              boxShadow: (theme) =>
                `0 4px 12px ${alpha(theme.palette.primary.main, 0.2)}`,
              "&:hover": {
                boxShadow: (theme) =>
                  `0 6px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
              },
            }}
          >
            Add
          </Button>
        </Stack>
      </Stack>

      <Tabs
        value={periodFilter}
        onChange={(_, newValue) => {
          setPeriodFilter(newValue);
          setIsExpanded(false);
        }}
        sx={{
          mb: 3,
          borderBottom: 1,
          borderColor: "divider",
          "& .MuiTab-root": {
            minHeight: 48,
            fontWeight: 700,
            textTransform: "none",
          },
        }}
      >
        <Tab label="Monthly" value="monthly" />
        <Tab label="Weekly" value="weekly" />
      </Tabs>

      {error ? (
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          Failed to load budgets.
        </Alert>
      ) : (
        <Stack spacing={4}>
          <BudgetSection
            title={`${periodFilter} Overview`}
            items={totalBudgets}
            viewMode={viewMode}
            onEdit={(b) => openModal("edit", b)}
            onDelete={(b) => openModal("delete", b)}
          />
          <Box>
            <BudgetSection
              title={`${periodFilter} Categories`}
              items={visibleCategories}
              viewMode={viewMode}
              onEdit={(b) => openModal("edit", b)}
              onDelete={(b) => openModal("delete", b)}
            />
            {categoryBudgets.length > 8 && (
              <Button
                fullWidth
                onClick={() => setIsExpanded(!isExpanded)}
                startIcon={isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                sx={{
                  mt: 3,
                  py: 1,
                  borderRadius: 2,
                  color: "text.secondary",
                  bgcolor: "grey.50",
                  fontWeight: 700,
                  textTransform: "none",
                  "&:hover": { bgcolor: "grey.100" },
                }}
              >
                {isExpanded
                  ? "Show Less"
                  : `View All ${periodFilter} Categories (${categoryBudgets.length})`}
              </Button>
            )}
            {categoryBudgets.length === 0 && totalBudgets.length === 0 && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: "center", py: 8 }}
              >
                No {periodFilter} budgets found. Click "Add" to get started.
              </Typography>
            )}
          </Box>
        </Stack>
      )}

      <BudgetModal
        open={modalState.type === "create" || modalState.type === "edit"}
        onClose={closeModal}
        budget={modalState.budget}
      />
      <DeleteBudgetDialog
        open={modalState.type === "delete"}
        onClose={closeModal}
        budget={modalState.budget}
      />
    </Paper>
  );
};

const BudgetSection = ({ title, items, viewMode, onEdit, onDelete }) => {
  if (items.length === 0) return null;
  return (
    <Box>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{
          mb: 2,
          fontWeight: 800,
          textTransform: "uppercase",
          display: "block",
          letterSpacing: 1.2,
        }}
      >
        {title}
      </Typography>
      {viewMode === "grid" ? (
        <Grid container spacing={3} alignItems="stretch">
          {items.map((budget) => (
            <Grid
              key={budget.id}
              item
              xs={12}
              sm={6}
              lg={3}
              sx={{
                display: "flex",
                justifyContent: "center",
              }}
            >
              <BudgetCard budget={budget} onEdit={onEdit} onDelete={onDelete} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper
          variant="outlined"
          sx={{ borderRadius: 3, overflow: "hidden", borderColor: "grey.200" }}
        >
          <List disablePadding>
            {items.map((budget, idx) => (
              <React.Fragment key={budget.id}>
                <BudgetRow
                  budget={budget}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
                {idx < items.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default BudgetManager;
