import { useState } from "react";
import { Box, Toolbar } from "@mui/material";
import Navbar from "../components/navigation/Navbar";

const MainLayout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  // Toggle mobile drawer -> needs to be implemented in the navbar
  const handleMobileDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: "flex" }}>
      {/* Navbar */}
      <Navbar handleMobileDrawerToggle={handleMobileDrawerToggle} />

      {/* Main Page Content */}
      <Box
        component="main"
        sx={{ display: "flex", flexDirection: "column", flexGrow: 1, p: 3 }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;
