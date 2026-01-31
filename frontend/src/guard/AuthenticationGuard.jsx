import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet } from "react-router-dom";
import { useEffect } from "react";
import { Box } from "@mui/material";
import PageLoader from "../components/common/PageLoader";

export const AuthenticationGuard = () => {
  const { isAuthenticated, isLoading, logout } = useAuth0();

  useEffect(() => {
    if (isLoading) return;

    const searchParams = new URLSearchParams(window.location.search);
    const isRedirecting = searchParams.has("code");

    if (isRedirecting) return;

    const isTabSessionActive = sessionStorage.getItem("app_session_active");

    if (isAuthenticated && !isTabSessionActive) {
      console.warn("Session mismatch detected (Zombie Tab). Logging out.");
      logout({ logoutParams: { returnTo: window.location.origin } });
    }

    if (isAuthenticated) {
      sessionStorage.setItem("app_session_active", "true");
    }
  }, [isAuthenticated, isLoading, logout]);

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
