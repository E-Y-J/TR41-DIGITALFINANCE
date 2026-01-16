import { Navigate, Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import PageLoader from "../components/PageLoader";
import { useGetUser } from "../hooks/queries/useGetUser";

export const UserGuard = () => {
  const { data: dbUser, isLoading } = useGetUser();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  console.log("DB User in UserGuard:", dbUser);
  console.log("Account Status:", dbUser?.data.account_status);

  // If user is stuck in "pending", force them to Onboarding
  if (dbUser?.data.account_status === "AccountStatus.PENDING") {
    return <Navigate to="/onboarding" replace />;
  }

  // If active, render the actual page (Home/Dashboard)
  return <Outlet />;
};
