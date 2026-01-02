import { useState } from "react";
import { Box, Toolbar, Drawer, IconButton } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

const drawerWidth = 240;

const DashboardLayout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: "flex" }}>
      {/* 1. The Top Bar */}
      <TopBar
        drawerWidth={drawerWidth}
        handleDrawerToggle={handleDrawerToggle}
      />

      {/* 2. The Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", sm: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
        >
          <Sidebar />
        </Drawer>

        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", sm: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
          open
        >
          <Sidebar />
        </Drawer>
      </Box>

      {/* 3. The Main Page Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {children}
        <Box
          sx={{
            position: "fixed",
            bottom: 16,
            right: 16,
          }}
        >
          <IconButton
            aria-label="chat-assistant"
            onClick={() => alert("Chat clicked!")}
            sx={{
              p: 1.5,
              backgroundColor: "primary.light",
              "&:hover": {
                backgroundColor: "primary.main",
              },
              boxShadow: 4,
            }}
          >
            <ChatIcon
              sx={{
                color: "white",
                fontSize: {
                  xs: 20,
                  sm: 30,
                },
              }}
            />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardLayout;
