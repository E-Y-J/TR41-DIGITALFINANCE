import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import HomePage from "./pages/HomePage";
import OnboardingPage from "./pages/OnboardingPage";

// Guards
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
        <Route element={<UserGuard />}>
          <Route path="/home" element={<HomePage />} />
        </Route>
      </Route>
    </Routes>
  );
};

export default App;
