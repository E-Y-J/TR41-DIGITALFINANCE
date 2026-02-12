import { useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Outlet, useLocation } from "react-router-dom";
import { useGetUser } from "../features/auth/useGetUser";
import {
  Box,
  Toolbar,
  Drawer,
  IconButton,
  Backdrop,
  useTheme,
  useMediaQuery,
  alpha,
  Drawer as MuiDrawer,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import ChatIcon from "@mui/icons-material/Chat";

import Sidebar from "./Sidebar";
import TopBar from "./Topbar";
import ChatBubble from "../features/chat";
import PageLoader from "../components/common/PageLoader";
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
  const location = useLocation();
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
    sessionStorage.removeItem("app_session_active");
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

  const isAiPage = location.pathname === "/home/ai-assistant";

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
          height: "100vh",
          display: "flex",
          overflow: "auto",
          flexDirection: "column",
          bgcolor: "background.default",
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 48, sm: 64 }, flexShrink: 0 }} />
        <Box sx={{ p: 3, pb: 0, flexShrink: 0 }}>
          <Breadcrumb />
        </Box>
        <Box sx={{ flexGrow: 1, minHeight: 0 }}>
          <Outlet />
        </Box>
        {/* Ai Assistant  */}

        {!isAiPage && (
          <>
            <Box
              sx={{
                position: "fixed",
                bottom: 16,
                right: 24,
                zIndex: 1200,
              }}
            >
              <IconButton
                aria-label="chat-assistant"
                onClick={handleChatDrawerToggle}
                sx={{
                  transition: "all 0.2s ease-in-out",
                  p: 1.5,
                  backgroundColor: (theme) =>
                    theme.palette.mode === "dark"
                      ? "primary.main"
                      : "primary.light",
                  color: "white",
                  boxShadow: (theme) =>
                    theme.palette.mode === "dark"
                      ? `0 8px 24px ${alpha(theme.palette.common.black, 0.6)}`
                      : 4,
                  "&:hover": {
                    backgroundColor: (theme) =>
                      theme.palette.mode === "dark"
                        ? "primary.light"
                        : "primary.main",
                    transform: "translateY(-4px)",
                    boxShadow: (theme) =>
                      theme.palette.mode === "dark"
                        ? `0 12px 32px ${alpha(theme.palette.common.black, 0.8)}`
                        : 6,
                  },
                }}
              >
                <ChatIcon sx={{ fontSize: 28 }} />
              </IconButton>
            </Box>

            <Drawer
              anchor="right"
              open={chatDrawerOpen}
              onClose={handleChatDrawerToggle}
              variant="temporary"
              sx={{
                "& .MuiDrawer-paper": {
                  boxSizing: "border-box",
                  width: { xs: "100%", sm: 400 },
                  borderTopLeftRadius: { xs: 0, sm: 24 },
                  borderBottomLeftRadius: { xs: 0, sm: 24 },
                  height: "100%",
                  bgcolor: "background.paper",
                  backgroundImage: "none",
                  borderLeft: (theme) =>
                    theme.palette.mode === "dark"
                      ? `1px solid ${theme.palette.divider}`
                      : "none",
                  boxShadow: (theme) =>
                    theme.palette.mode === "dark"
                      ? "-8px 0 32px rgba(0,0,0,0.5)"
                      : "-4px 0 24px rgba(0,0,0,0.1)",
                },
              }}
            >
              <ChatBubble
                handleChatDrawerToggle={handleChatDrawerToggle}
                user={user}
              />
            </Drawer>
          </>
        )}
      </Box>
      {/* Global Loader */}
      <Backdrop
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 999,
          backgroundColor: (theme) =>
            theme.palette.mode === "dark"
              ? "rgba(15, 23, 42, 0.8)"
              : "rgba(255, 255, 255, 0.8)",
        }}
        open={isGlobalLoading || isLoading}
      >
        <PageLoader sx={{ bgcolor: "transparent" }} />
      </Backdrop>
    </Box>
  );
};

export default DashboardLayout;
