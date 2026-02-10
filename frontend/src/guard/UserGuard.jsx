import { Navigate, Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import PageLoader from "../components/common/PageLoader";
import { useGetUser } from "../features/auth/useGetUser";

export const UserGuard = () => {
  const { data: user, isLoading } = useGetUser();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  // Handle case where user data is not yet available
  if (!user) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  if (user.account_status === "pending") {
    return <Navigate to="/onboarding" replace />;
  }

  return <Outlet />;
};
