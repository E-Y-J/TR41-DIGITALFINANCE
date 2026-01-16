import { Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import PageLoader from "./components/PageLoader";
import DashboardLayout from "./layouts/DashboardLayout";

import { AuthenticationGuard } from "./guard/AuthenticationGuard";
import { UserGuard } from "./guard/UserGuard";
import { PublicRoute } from "./guard/PublicRoute";

// Lazy Import to reduce initial bundle size
const LandingPage = lazy(() => import("./pages/LandingPage"));
const OnboardingPage = lazy(() => import("./pages/OnboardingPage"));
const HomePage = lazy(() => import("./pages/HomePage"));
const BudgetPage = lazy(() => import("./pages/BudgetPage"));
const TransactionPage = lazy(() => import("./pages/TransactionPage"));
const AiAssistantPage = lazy(() => import("./pages/AiAssistantPage"));

const App = () => {
  return (
    <Routes>
      {/* PUBLIC ROUTES */}
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

      {/* AUTHENTICATED ROUTES */}
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
