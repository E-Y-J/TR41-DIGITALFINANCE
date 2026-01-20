import { Button } from "@mui/material";
import DashboardWidget from "../../components/common/DashboardWidget";
import TransactionTable from "./TransactionTable";
import { useGetTransactions } from "./useGetTransactions";
import CircularProgress from "@mui/material/CircularProgress";
import { Box, Typography } from "@mui/material";

const RecentTransactionsWidget = () => {
  const { data, isLoading, isError } = useGetTransactions({
    per_page: 5,
    sort_by: "date",
    sort_order: "desc",
  });

  if (isLoading) {
    return (
      <DashboardWidget title="Transaction History" sx={{ minHeight: 450 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            width: "100%",
            height: "100%",
          }}
        >
          <CircularProgress size={55} color="primary" />
        </Box>
      </DashboardWidget>
    );
  }

  // improve error handling later
  if (isError) {
    return (
      <DashboardWidget title="Transaction History" sx={{ minHeight: 450 }}>
        <Typography color="error" align="center" sx={{ py: 4 }}>
          Failed to load transactions.
        </Typography>
      </DashboardWidget>
    );
  }

  return (
    <DashboardWidget
      title="Transaction History"
      sx={{ minHeight: 450 }}
      action={
        <Button
          size="small"
          sx={{
            textTransform: "none",
            fontWeight: 600,
            borderRadius: 2,
          }}
        >
          View All
        </Button>
      }
    >
      <TransactionTable data={data} />
    </DashboardWidget>
  );
};

export default RecentTransactionsWidget;
