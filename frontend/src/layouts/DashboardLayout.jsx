import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Outlet } from "react-router-dom";
import { useGetUser } from "../hooks/queries/useGetUser";
import {
  Box,
  Toolbar,
  Drawer,
  IconButton,
  Backdrop,
  useTheme,
  useMediaQuery,
  Drawer as MuiDrawer,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import ChatIcon from "@mui/icons-material/Chat";

import Sidebar from "../components/navigation/Sidebar";
import TopBar from "../components/navigation/Topbar";
import ChatBubble from "../components/dashboard/Chat";
import PageLoader from "../components/PageLoader";
import Breadcrumb from "../components/common/Breadcrumb";

const drawerWidth = 240;

const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: "hidden",
});

const closedMixin = (theme) => ({
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: "hidden",
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up("sm")]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const StyledDrawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: "nowrap",
  boxSizing: "border-box",
  variants: [
    {
      props: ({ open }) => open,
      style: {
        ...openedMixin(theme),
        "& .MuiDrawer-paper": openedMixin(theme),
      },
    },
    {
      props: ({ open }) => !open,
      style: {
        ...closedMixin(theme),
        "& .MuiDrawer-paper": closedMixin(theme),
      },
    },
  ],
}));

const DashboardLayout = () => {
  const { logout } = useAuth0();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const { data: user, isLoading } = useGetUser();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopOpen, setDesktopOpen] = useState(false);
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false);
  const [isGlobalLoading, setIsGlobalLoading] = useState(false);

  const handleLogout = () => {
    setIsGlobalLoading(true);
    setTimeout(() => {
      logout({ logoutParams: { returnTo: window.location.origin } });
    }, 500);
  };

  const handleMobileDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleChatDrawerToggle = () => {
    setChatDrawerOpen(!chatDrawerOpen);
  };

  return (
    <Box sx={{ display: "flex" }}>
      {/* Top Bar */}
      <TopBar
        drawerWidth={drawerWidth}
        handleMobileDrawerToggle={handleMobileDrawerToggle}
        handleLogout={handleLogout}
        open={isMobile ? false : desktopOpen}
        user={user}
      />

      {/* Nav Sidebar */}
      <Box component="nav">
        {isMobile ? (
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
            <Sidebar handleLogout={handleLogout} user={user} />
          </Drawer>
        ) : (
          <StyledDrawer
            variant="permanent"
            open={desktopOpen}
            onMouseEnter={() => setDesktopOpen(true)}
            onMouseLeave={() => setDesktopOpen(false)}
            sx={{
              display: { xs: "none", sm: "block" },
            }}
          >
            <Sidebar open={desktopOpen} />
          </StyledDrawer>
        )}
      </Box>

      {/* Main Page */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          minHeight: "100vh",
          overflow: "auto",
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 48, sm: 64 } }} />
        <Box sx={{ mb: 2 }}>
          <Breadcrumb />
        </Box>
        <Outlet />
        {/* Ai Assistant  */}
        <Box sx={{ position: "fixed", bottom: 16, right: 16 }}>
          <IconButton
            aria-label="chat-assistant"
            onClick={handleChatDrawerToggle}
            sx={{
              transition: "transform 0.15s ease-in-out",
              p: 1.5,
              backgroundColor: "primary.light",
              color: "white",
              boxShadow: 4,
              "&:hover": {
                backgroundColor: "primary.main",
                transform: "translateY(-3px)",
                boxShadow: 2,
              },
            }}
          >
            <ChatIcon sx={{ fontSize: { xs: 20, sm: 30 } }} />
          </IconButton>
        </Box>
        <Drawer
          anchor="right"
          variant="persistent"
          open={chatDrawerOpen}
          onClose={handleChatDrawerToggle}
          sx={{
            width: { xs: drawerWidth, sm: drawerWidth * 1.2 },
            flexShrink: 0,
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              borderRadius: "24px 0 0 24px",
              width: {
                xs: drawerWidth,
                sm: drawerWidth * 1.2,
                md: drawerWidth * 1.4,
              },
              borderLeft: "2px solid",
              borderColor: "divider",
            },
          }}
        >
          <ChatBubble handleChatDrawerToggle={handleChatDrawerToggle} />
        </Drawer>
      </Box>

      {/* Global Loader */}
      <Backdrop
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 999,
          color: "#fff",
          backgroundColor: "rgba(255, 255, 255, 0.8)",
        }}
        open={isGlobalLoading || isLoading}
      >
        <PageLoader />
      </Backdrop>
    </Box>
  );
};

export default DashboardLayout;
