import DashboardWidget from "../../components/common/DashboardWidget";
import LoanTracker from "./LoanTracker";

const ActiveLoansWidget = () => {
  return (
    <DashboardWidget title="Active Loans" sx={{ minHeight: 450 }}>
      <LoanTracker />
    </DashboardWidget>
  );
};

export default ActiveLoansWidget;
