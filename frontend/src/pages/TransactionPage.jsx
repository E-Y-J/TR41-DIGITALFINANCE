import { Box, Paper } from "@mui/material";
import TransactionFilters from "../features/transactions/components/TransactionFilters";
import TransactionToolbar from "../features/transactions/components/TransactionToolbar";
import TransactionList from "../features/transactions/components/TransactionList";
import { useTransactionsPage } from "../hooks/useTransactionsPage";

export default function TransactionsPage() {
  const {
    transactions,
    totalCount,
    isLoading,
    filters,
    page,
    rowsPerPage,
    onFilterChange,
    onPageChange,
    onRowsPerPageChange,
  } = useTransactionsPage();

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <TransactionToolbar filters={filters} onFilterChange={onFilterChange} />

      <Paper
        elevation={3}
        sx={{
          p: { xs: 2, sm: 3 },
          borderRadius: 4,
          border: "1px solid",
          borderColor: "grey.200",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Box sx={{ mb: 2 }}>
          <TransactionFilters
            filters={filters}
            onFilterChange={onFilterChange}
          />
        </Box>

        <Box sx={{ width: "100%" }}>
          <TransactionList
            transactions={transactions}
            totalCount={totalCount}
            page={page}
            rowsPerPage={rowsPerPage}
            onPageChange={onPageChange}
            onRowsPerPageChange={onRowsPerPageChange}
            isLoading={isLoading}
          />
        </Box>
      </Paper>
    </Box>
  );
}
