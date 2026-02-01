import { Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import PageLoader from "./components/common/PageLoader";
import DashboardLayout from "./layouts/DashboardLayout";

import { AuthenticationGuard } from "./guard/AuthenticationGuard";
import { UserGuard } from "./guard/UserGuard";
import { PublicRoute } from "./guard/PublicRoute";

// Lazy Import
const LandingPage = lazy(() => import("./pages/LandingPage"));
const OnboardingPage = lazy(() => import("./pages/OnboardingPage"));
const HomePage = lazy(() => import("./pages/HomePage"));
const BudgetPage = lazy(() => import("./pages/BudgetPage"));
const TransactionPage = lazy(() => import("./pages/TransactionPage"));
const AiAssistantPage = lazy(() => import("./pages/AiAssistantPage"));

const CallbackPage = () => {
  return <PageLoader />;
};

const App = () => {
  return (
    <Routes>
      {/* 1. PUBLIC ROUTES */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <Suspense fallback={<PageLoader />}>
              <LandingPage />
            </Suspense>
          </PublicRoute>
        }
      />

      {/* 2. CALLBACK ROUTE  */}
      <Route path="/callback" element={<CallbackPage />} />

      {/* 3. AUTHENTICATED ROUTES */}
      <Route element={<AuthenticationGuard />}>
        <Route
          path="/onboarding"
          element={
            <Suspense fallback={<PageLoader />}>
              <OnboardingPage />
            </Suspense>
          }
        />

        {/* DASHBOARD ROUTES */}
        <Route element={<UserGuard />}>
          <Route element={<DashboardLayout />}>
            <Route path="/home" element={<HomePage />} />
            <Route path="/home/budget" element={<BudgetPage />} />
            <Route path="/home/transactions" element={<TransactionPage />} />
            <Route path="/home/ai-assistant" element={<AiAssistantPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
};

export default App;
