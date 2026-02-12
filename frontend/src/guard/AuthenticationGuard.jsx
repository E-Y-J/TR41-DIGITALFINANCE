import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Outlet } from "react-router-dom";
import { useEffect } from "react";
import PageLoader from "../components/common/PageLoader";

export const AuthenticationGuard = () => {
  const { isAuthenticated, isLoading } = useAuth0();

  useEffect(() => {
    if (isLoading) return;

    const searchParams = new URLSearchParams(window.location.search);
    const isRedirecting = searchParams.has("code");

    if (isRedirecting) return;

    if (isAuthenticated) {
      sessionStorage.setItem("app_session_active", "true");
    }
  }, [isAuthenticated, isLoading]);

  if (isLoading) {
    return <PageLoader absolute />;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/" replace />;
};
