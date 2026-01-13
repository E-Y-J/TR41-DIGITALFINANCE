import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";
import { Box } from "@mui/material";
import PageLoader from "../components/PageLoader";

// do we want users who are logged in to still see the marketing of the landing page?
export const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/home" replace />;
  }

  return children;
};
