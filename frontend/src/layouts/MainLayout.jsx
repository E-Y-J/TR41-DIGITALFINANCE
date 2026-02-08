import { Box, Toolbar } from "@mui/material";
import Navbar from "./Navbar";
import Footer from "../features/landing/Footer";

const MainLayout = ({ children }) => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      {/* Navbar */}
      <Navbar />

      {/* Main Page Content */}
      <Box
        component="main"
        sx={{ display: "flex", flexDirection: "column", flexGrow: 1, p: 3 }}
      >
        <Toolbar />
        {children}
      </Box>

      {/* Footer */}
      <Box component="footer" sx={{ width: "100%", mt: "auto" }}>
        <Footer />
      </Box>
    </Box>
  );
};

export default MainLayout;
