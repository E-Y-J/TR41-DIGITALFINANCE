import { Navigate, Outlet } from "react-router-dom";
import PageLoader from "../components/common/PageLoader";
import { useGetUser } from "../features/auth/useGetUser";

export const UserGuard = () => {
  const { data: user, isLoading } = useGetUser();

  if (isLoading) {
    return <PageLoader absolute />;
  }

  if (!user) {
    return <PageLoader absolute />;
  }

  if (user.account_status === "pending") {
    return <Navigate to="/onboarding" replace />;
  }

  return <Outlet />;
};
