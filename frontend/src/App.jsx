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
const NotFound = lazy(() => import("./pages/NotFound"));

const App = () => {
  return (
    <Routes>
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

      <Route path="/callback" element={<PageLoader />} />

      <Route element={<AuthenticationGuard />}>
        <Route
          path="/onboarding"
          element={
            <Suspense fallback={<PageLoader />}>
              <OnboardingPage />
            </Suspense>
          }
        />

        <Route element={<UserGuard />}>
          <Route element={<DashboardLayout />}>
            <Route path="/home" element={<HomePage />} />
            <Route path="/home/budget" element={<BudgetPage />} />
            <Route path="/home/transactions" element={<TransactionPage />} />
            <Route path="/home/ai-assistant" element={<AiAssistantPage />} />
            <Route
              path="/home/*"
              element={
                <Suspense fallback={<PageLoader />}>
                  <NotFound />
                </Suspense>
              }
            />
          </Route>
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <Suspense fallback={<PageLoader />}>
            <NotFound />
          </Suspense>
        }
      />
    </Routes>
  );
};

export default App;
