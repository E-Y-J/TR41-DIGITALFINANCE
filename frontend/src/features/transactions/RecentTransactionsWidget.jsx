import { Button } from "@mui/material";
import DashboardWidget from "../../components/common/DashboardWidget";
import TransactionTable from "./TransactionTable";
import { useGetTransactions } from "./useGetTransactions";

const RecentTransactionsWidget = () => {
  const { data, isLoading, isError } = useGetTransactions({
    per_page: 5,
    sort_by: "date",
    sort_order: "desc",
  });

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
      <TransactionTable />
    </DashboardWidget>
  );
};

export default RecentTransactionsWidget;
