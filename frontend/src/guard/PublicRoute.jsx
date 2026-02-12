import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";
import PageLoader from "../components/common/PageLoader";

export const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <PageLoader absolute />;
  }

  if (isAuthenticated) {
    return <Navigate to="/home" replace />;
  }

  return children;
};
