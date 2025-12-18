import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import { AuthenticationGuard, PublicRoute } from "./guard";

const App = () => {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />
      <Route
        path="/home"
        element={
          <AuthenticationGuard>
            <HomePage />
          </AuthenticationGuard>
        }
      />
    </Routes>
  );
};

export default App;
