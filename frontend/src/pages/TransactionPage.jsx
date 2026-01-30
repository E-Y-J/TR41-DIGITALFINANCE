import { useState, useEffect } from "react";
import { Box, Paper } from "@mui/material";

import TransactionFilters from "../features/transactions/components/TransactionFilters";
import TransactionToolbar from "../features/transactions/components/TransactionToolbar";
import TransactionList from "../features/transactions/components/TransactionList";

export default function TransactionsPage() {
  const [filters, setFilters] = useState({
    search: "",
    category: "All",
    type: "All",
  });
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search);
  const [page, setPage] = useState(0);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 500);

    return () => clearTimeout(handler);
  }, [filters.search]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(0);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <TransactionToolbar
        filters={filters}
        onFilterChange={handleFilterChange}
      />
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
        <Box sx={{ bgcolor: "white" }}>
          <TransactionFilters
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        </Box>
        <Box sx={{ width: "100%" }}>
          <TransactionList
            filters={{ ...filters, search: debouncedSearch }}
            page={page}
            setPage={setPage}
          />
        </Box>
      </Paper>
    </Box>
  );
}
