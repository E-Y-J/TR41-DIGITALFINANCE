import { useState } from "react";
import { Box, CircularProgress, TablePagination } from "@mui/material";
import TransactionTable from "./TransactionTable";
import { useGetTransactions } from "../useGetTransactions";

export const TransactionList = ({ filters, page, setPage }) => {
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // can implement filter by start and end date, sort by, sort order later
  // by searching isn't implemented in the backend yet
  const { data, isLoading, isFetching } = useGetTransactions({
    page: page + 1,
    per_page: rowsPerPage,
    search: filters.search,
    category: filters.category === "All" ? "" : filters.category,
    transaction_type: filters.type === "All" ? "" : filters.type,
  });

  console.log(data);

  const transactions = data?.items || [];

  return (
    <Box sx={{ width: "100%" }}>
      {isLoading || isFetching ? (
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
