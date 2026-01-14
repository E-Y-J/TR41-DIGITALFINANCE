import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  IconButton,
  Box,
  Badge,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";
import NotificationsIcon from "@mui/icons-material/Notifications";
import AccountCircle from "@mui/icons-material/AccountCircle";
import PersonIcon from "@mui/icons-material/Person";
import SettingsIcon from "@mui/icons-material/Settings";
import LogoutIcon from "@mui/icons-material/Logout";

const TopBar = ({
  drawerWidth,
  handleMobileDrawerToggle,
  handleLogout,
  open,
}) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const isMenuOpen = Boolean(anchorEl);

  const miniDrawerWidth = 65;

  const SETTINGS_ITEMS = [
    {
      text: "My Profile",
      icon: <PersonIcon fontSize="small" />,
      path: "/settings/profile",
    },
    {
      text: "Settings",
      icon: <SettingsIcon fontSize="small" />,
      path: "/settings/account",
    },
    {
      text: "Logout",
      icon: <LogoutIcon fontSize="small" />,
      onClick: handleLogout,
    },
  ];

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);

  const handleMenuClose = () => setAnchorEl(null);

  const handleMenuItemClick = (item) => {
    handleMenuClose();
    if (item.onClick) item.onClick();
    else if (item.path) navigate(item.path);
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        bgcolor: "background.paper",
        color: "text.primary",
        borderBottom: "1px solid",
        borderColor: "divider",
        zIndex: (theme) => theme.zIndex.drawer + 1,
        transition: (theme) =>
          theme.transitions.create(["width", "margin"], {
            easing: theme.transitions.easing.sharp,
            duration: open
              ? theme.transitions.duration.enteringScreen
              : theme.transitions.duration.leavingScreen,
          }),

        width: {
          sm: open
            ? `calc(100% - ${drawerWidth}px)`
            : `calc(100% - ${miniDrawerWidth}px)`,
        },
        ml: {
          sm: open ? `${drawerWidth}px` : `${miniDrawerWidth}px`,
        },
      }}
    >
      <Toolbar>
        {/* Mobile Hamburger */}
        <IconButton
          color="inherit"
          edge="start"
          onClick={handleMobileDrawerToggle}
          sx={{ mr: 2, display: { sm: "none" } }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ flexGrow: 1 }} />

        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton size="large" color="inherit" sx={{ mr: 1 }}>
            <Badge variant="dot" color="error" overlap="circular">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User Menu */}
        <Box sx={{ display: { xs: "none", sm: "block" } }}>
          <Tooltip title="Account settings">
            <IconButton onClick={handleMenuOpen} size="small" sx={{ ml: 0.5 }}>
              <AccountCircle sx={{ width: 32, height: 32 }} />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorEl}
            open={isMenuOpen}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
            slotProps={{
              paper: {
                elevation: 0,
                sx: {
                  overflow: "visible",
                  filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
                  mt: 1.5,
                  "&::before": {
                    content: '""',
                    display: "block",
                    position: "absolute",
                    top: 0,
                    right: 14,
                    width: 10,
                    height: 10,
                    bgcolor: "background.paper",
                    transform: "translateY(-50%) rotate(45deg)",
                    zIndex: 0,
                  },
                },
              },
            }}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
          >
            {SETTINGS_ITEMS.map((item) => (
              <MenuItem
                key={item.text}
                onClick={() => handleMenuItemClick(item)}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText>{item.text}</ListItemText>
              </MenuItem>
            ))}
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
