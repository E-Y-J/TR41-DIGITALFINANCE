import { useState } from "react";
import { Box, Toolbar, Drawer, IconButton, Button } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import ChatBubble from "../components/ChatBubble";

const drawerWidth = 240;

const DashboardLayout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false);

  const handleMobileDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleChatDrawerToggle = () => {
    setChatDrawerOpen(!chatDrawerOpen);
  };

  return (
    <Box sx={{ display: "flex" }}>
      {/* 1. The Top Bar */}
      <TopBar
        drawerWidth={drawerWidth}
        handleMobileDrawerToggle={handleMobileDrawerToggle}
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
          onClose={handleMobileDrawerToggle}
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
        <Button
          variant="contained"
          onClick={handleChatDrawerToggle}
          sx={{ mt: 2 }}
        >
          {chatDrawerOpen ? "Close Chat Assistant" : "Open Chat Assistant"}
        </Button>
        <Box
          sx={{
            position: "fixed",
            bottom: 16,
            right: 16,
          }}
        >
          <IconButton
            aria-label="chat-assistant"
            onClick={handleChatDrawerToggle}
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
        <Drawer
          anchor="right"
          variant="persistent"
          open={chatDrawerOpen}
          onClose={handleChatDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            width: {
              xs: drawerWidth,
              sm: drawerWidth * 1.2,
            },
            flexShrink: 0,
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              borderRadius: "24px 0 0 24px",
              width: {
                xs: drawerWidth,
                sm: drawerWidth * 1.2,
              },
              borderLeftWidth: "2px",
              borderLeftColor: "divider",
            },
          }}
        >
          <ChatBubble handleChatDrawerToggle={handleChatDrawerToggle} />
        </Drawer>
      </Box>
    </Box>
  );
};

export default DashboardLayout;
