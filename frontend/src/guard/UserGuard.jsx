import { Navigate, Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import PageLoader from "../components/PageLoader";
import { useGetUser } from "../hooks/queries/useGetUser";

export const UserGuard = () => {
  const { data: user, isLoading } = useGetUser();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  if (user.account_status === "AccountStatus.PENDING") {
    return <Navigate to="/onboarding" replace />;
  }

  return <Outlet />;
};
