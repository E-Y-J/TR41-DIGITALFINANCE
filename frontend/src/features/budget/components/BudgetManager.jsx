import { useState, useMemo } from "react";
import {
  Box,
  Paper,
  Stack,
  Tabs,
  Tab,
  Button,
  useTheme,
  useMediaQuery,
  CircularProgress,
  Alert,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

import { useGetBudgets } from "../useGetBudgets";
import BudgetHeader from "./BudgetHeader";
import OverviewSection from "./OverviewSection";
import CategoryGrid from "./CategoryGrid";
import BudgetModal from "./BudgetModal";
import DeleteBudgetDialog from "./DeleteBudgetDialog";

const BudgetManager = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const INITIAL_LIMIT = 3;

  const { data, isLoading, error } = useGetBudgets();
  const meta = data?.meta || {};

  const [viewMode, setViewMode] = useState("grid");
  const [periodFilter, setPeriodFilter] = useState("monthly");
  const [displayLimit, setDisplayLimit] = useState(INITIAL_LIMIT);
  const [modalState, setModalState] = useState({ type: null, budget: null });
  const effectiveViewMode = isMobile ? "list" : viewMode;

  console.log(data);

  const { totalBudgets, categoryBudgets, activeMeta } = useMemo(() => {
    const rawItems = data?.items || [];

    const filtered = rawItems.filter((b) => b.period === periodFilter);

    const totals = filtered.filter((b) => b.budget_type === "total");
    const categories = filtered.filter((b) => b.budget_type === "category");

    const exceeded = categories.filter((b) => b.is_exceeded).length;
    const warning = categories.filter(
      (b) => b.is_warning && !b.is_exceeded,
    ).length;
    const healthy = categories.length - exceeded - warning;

    return {
      totalBudgets: totals,
      categoryBudgets: categories,
      activeMeta: {
        exceeded_count: exceeded,
        warning_count: warning,
        healthy_count: healthy,
        total_categories: categories.length,
      },
    };
  }, [data, periodFilter]);

  const visibleCategories = useMemo(
    () => categoryBudgets.slice(0, displayLimit),
    [categoryBudgets, displayLimit],
  );

  const handleToggleLimit = () => {
    setDisplayLimit(
      displayLimit > INITIAL_LIMIT ? INITIAL_LIMIT : categoryBudgets.length,
    );
  };

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
        borderColor: "divider",
        bgcolor: "background.paper",
        backgroundImage: "none",
      }}
    >
      <BudgetHeader
        meta={meta}
        periodFilter={periodFilter}
        viewMode={effectiveViewMode}
        setViewMode={setViewMode}
        isMobile={isMobile}
        onAdd={() => setModalState({ type: "create", budget: null })}
      />

      <Tabs
        value={periodFilter}
        onChange={(_, v) => setPeriodFilter(v)}
        sx={{ mb: 3, borderBottom: 1, borderColor: "divider" }}
      >
        <Tab
          label="Monthly"
          value="monthly"
          sx={{ fontWeight: 700, textTransform: "none" }}
        />
        <Tab
          label="Weekly"
          value="weekly"
          sx={{ fontWeight: 700, textTransform: "none" }}
        />
      </Tabs>

      {error ? (
        <Alert severity="error">Failed to load budgets.</Alert>
      ) : (
        <Stack spacing={5}>
          {totalBudgets[0] && (
            <OverviewSection
              budget={totalBudgets[0]}
              meta={activeMeta}
              onEdit={(b) => setModalState({ type: "edit", budget: b })}
              onDelete={(b) => setModalState({ type: "delete", budget: b })}
            />
          )}

          <Box>
            <CategoryGrid
              items={visibleCategories}
              viewMode={effectiveViewMode}
              onEdit={(b) => setModalState({ type: "edit", budget: b })}
              onDelete={(b) => setModalState({ type: "delete", budget: b })}
            />

            {categoryBudgets.length > INITIAL_LIMIT && (
              <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
                <Button
                  variant="outlined"
                  onClick={handleToggleLimit}
                  startIcon={
                    displayLimit > INITIAL_LIMIT ? (
                      <ExpandLessIcon />
                    ) : (
                      <ExpandMoreIcon />
                    )
                  }
                  sx={{ fontWeight: 800, borderRadius: 3, px: 4 }}
                >
                  {displayLimit > INITIAL_LIMIT
                    ? "Show Less"
                    : "View All Categories"}
                </Button>
              </Box>
            )}
          </Box>
        </Stack>
      )}

      <BudgetModal
        open={modalState.type === "create" || modalState.type === "edit"}
        onClose={() => setModalState({ type: null, budget: null })}
        budget={modalState.budget}
      />
      <DeleteBudgetDialog
        open={modalState.type === "delete"}
        onClose={() => setModalState({ type: null, budget: null })}
        budget={modalState.budget}
      />
    </Paper>
  );
};

export default BudgetManager;
