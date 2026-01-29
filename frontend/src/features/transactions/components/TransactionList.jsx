import { useState } from "react";
import { Box, CircularProgress, TablePagination } from "@mui/material";
import TransactionTable from "./TransactionTable";
import { useGetTransactions } from "../useGetTransactions";

export const TransactionList = ({ filters, page, setPage }) => {
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const { data, isLoading } = useGetTransactions({
    page: page + 1,
    per_page: rowsPerPage,
    search: filters.search,
    category: filters.category === "All" ? "" : filters.category,
    type: filters.type === "All" ? "" : filters.type,
  });

  const transactions = data?.items || [];

  return (
    <Box sx={{ width: "100%" }}>
      {isLoading ? (
        <Box sx={{ p: 6, textAlign: "center" }}>
          <CircularProgress size={40} />
        </Box>
      ) : (
        <>
          <TransactionTable data={transactions} />
          <TablePagination
            component="div"
            count={data?.total || 0}
            page={page}
            onPageChange={(event, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            sx={{ borderTop: "1px solid", borderColor: "divider" }}
          />
        </>
      )}
    </Box>
  );
};

export default TransactionList;
