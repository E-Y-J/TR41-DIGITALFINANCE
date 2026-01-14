import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import HomePage from "./pages/HomePage";
import OnboardingPage from "./pages/OnboardingPage";
import BudgetPage from "./pages/BudgetPage";
import TransactionPage from "./pages/TransactionPage";
import AiAssistantPage from "./pages/AiAssistantPage";
import DashboardLayout from "./layouts/DashboardLayout";

import { AuthenticationGuard } from "./guard/AuthenticationGuard";
import { UserGuard } from "./guard/UserGuard";
import { PublicRoute } from "./guard/PublicRoute";

const App = () => {
  return (
    <Routes>
      {/*  PUBLIC ROUTES  */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />

      {/*   MUST BE LOGGED IN  */}
      <Route element={<AuthenticationGuard />}>
        <Route path="/onboarding" element={<OnboardingPage />} />

        {/*   MUST BE "ACTIVE" STATUS  */}
        {/* <Route element={<UserGuard />}> removed for testing purpose */}
        {/* The Layout stays mounted for all these paths */}
        <Route element={<DashboardLayout />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/home/budget" element={<BudgetPage />} />
          <Route path="/home/transactions" element={<TransactionPage />} />
          <Route path="/home/ai-assistant" element={<AiAssistantPage />} />
        </Route>
        {/* </Route> */}
      </Route>
    </Routes>
  );
};

export default App;
