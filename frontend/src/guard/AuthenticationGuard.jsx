import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet } from "react-router-dom";
import { useEffect } from "react";
import { Box } from "@mui/material";
import PageLoader from "../components/common/PageLoader";

export const AuthenticationGuard = () => {
  const { isAuthenticated, isLoading } = useAuth0();

  useEffect(() => {
    if (isLoading) return;

    const searchParams = new URLSearchParams(window.location.search);
    const isRedirecting = searchParams.has("code");

    if (isRedirecting) return;

    // Set session marker FIRST when authenticated
    // This prevents false-positive "zombie tab" detection on navigation
    if (isAuthenticated) {
      sessionStorage.setItem("app_session_active", "true");
    }
  }, [isAuthenticated, isLoading]);

  if (isLoading) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <PageLoader />
      </Box>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
};
