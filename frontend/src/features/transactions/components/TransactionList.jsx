import { Box, CircularProgress, TablePagination } from "@mui/material";
import TransactionTable from "./TransactionTable";

const TransactionList = ({
  transactions,
  totalCount,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  isLoading,
}) => {
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
            count={totalCount}
            page={page}
            onPageChange={onPageChange}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={onRowsPerPageChange}
            sx={{ borderTop: "1px solid", borderColor: "divider" }}
          />
        </>
      )}
    </Box>
  );
};

export default TransactionList;
