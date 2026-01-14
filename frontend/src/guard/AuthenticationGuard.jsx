import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import PageLoader from "../components/PageLoader";

export const AuthenticationGuard = () => {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
};
