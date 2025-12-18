import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import { AuthenticationGuard } from "./guard/AuthenticationGuard.jsx";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
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
