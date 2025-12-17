import { useAuth0 } from "@auth0/auth0-react";
import { Box } from "@mui/material";
import PageLoader from "../components/PageLoader.jsx";
import { Navigate } from "react-router-dom";

export const AuthenticationGuard = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <Box sx={{ height: "100vh" }}>
        <PageLoader />
      </Box>
    );
  }
  return isAuthenticated ? children : <Navigate to="/" />;
};
