import { Box, Paper } from "@mui/material";
import TransactionFilters from "../features/transactions/components/TransactionFilters";
import TransactionToolbar from "../features/transactions/components/TransactionToolbar";
import TransactionList from "../features/transactions/components/TransactionList";
import { useTransactionsPage } from "../hooks/useTransactionsPage";

export default function TransactionsPage() {
  const c = useTransactionsPage();

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <TransactionToolbar
        filters={c.filters}
        onFilterChange={c.onFilterChange}
      />
      <Paper
        elevation={3}
        sx={{
          p: { xs: 2, sm: 3 },
          borderRadius: 4,
          border: "1px solid",
          borderColor: "divider",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Box sx={{ mb: 2 }}>
          <TransactionFilters
            filters={c.filters}
            onFilterChange={c.onFilterChange}
          />
        </Box>

        <Box sx={{ width: "100%" }}>
          <TransactionList
            transactions={c.transactions}
            totalCount={c.totalCount}
            page={c.page}
            rowsPerPage={c.rowsPerPage}
            onPageChange={c.onPageChange}
            onRowsPerPageChange={c.onRowsPerPageChange}
            isLoading={c.isLoading}
          />
        </Box>
      </Paper>
    </Box>
  );
}
