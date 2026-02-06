import { Box, Typography, Button, CircularProgress } from "@mui/material";
import DashboardWidget from "../../components/common/DashboardWidget";
import LoanTracker from "./components/LoanTracker";
import { useGetLoans } from "./useGetLoans";

const ActiveLoansWidget = () => {
  const { data, isLoading, isError } = useGetLoans({
    // status: "open",
    // turned off so I can render all 5 loans for screen testing
  });
  const loans = data?.items || [];

  const navigateToAllLoans = () => {
    console.log("Navigate to all loans");
  };

  if (isError) {
    return (
      <DashboardWidget title="Active Loans" sx={{ minHeight: 450 }}>
        <Typography color="error" align="center" sx={{ py: 4 }}>
          Failed to load your active loans.
        </Typography>
      </DashboardWidget>
    );
  }

  if (isLoading) {
    return (
      <DashboardWidget title="Active Loans" sx={{ minHeight: 450 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            width: "100%",
          }}
        >
          <CircularProgress size={50} thickness={4.5} />
        </Box>
      </DashboardWidget>
    );
  }

  return (
    <DashboardWidget
      title="Your Active Loans"
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
      action={
        <Button
          size="small"
          variant="outlined"
          sx={{
            textTransform: "none",
            fontWeight: 600,
            borderRadius: 2,
            "&:hover": {
              bgcolor: "primary.main",
              color: "#ffffff",
              borderColor: "primary.main",
            },
          }}
          onClick={navigateToAllLoans}
        >
          View All
        </Button>
      }
    >
      <Box
        sx={{
          height: "100%",
          minHeight: 0,
        }}
      >
        <LoanTracker loans={loans} />
      </Box>
    </DashboardWidget>
  );
};

export default ActiveLoansWidget;
