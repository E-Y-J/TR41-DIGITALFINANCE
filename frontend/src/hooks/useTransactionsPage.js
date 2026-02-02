import { useState, useEffect } from "react";
import { useGetTransactions } from "../features/transactions/useGetTransactions";

export const useTransactionsPage = () => {
  const [filters, setFilters] = useState({
    search: "",
    category: "All",
    type: "All",
    sort_by: "date",
    sort_order: "desc",
  });
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(filters.search);
      setPage(0);
    }, 500);
    return () => clearTimeout(handler);
  }, [filters.search]);

  const { data, isLoading, isFetching } = useGetTransactions({
    page: page + 1,
    per_page: rowsPerPage,
    search: debouncedSearch,
    category: filters.category === "All" ? "" : filters.category,
    transaction_type: filters.type === "All" ? "" : filters.type,
  });

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return {
    transactions: data?.items || [],
    totalCount: data?.total || 0,
    isLoading: isLoading || isFetching,
    filters,
    page,
    rowsPerPage,
    onFilterChange: handleFilterChange,
    onPageChange: handlePageChange,
    onRowsPerPageChange: handleRowsPerPageChange,
  };
};
