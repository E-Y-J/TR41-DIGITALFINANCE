import { useLocation, useNavigate } from "react-router-dom";
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";

import TimelineIcon from "@mui/icons-material/Timeline";
import PaymentIcon from "@mui/icons-material/Payment";
import PieChartIcon from "@mui/icons-material/PieChart";
import AssistantIcon from "@mui/icons-material/Assistant";
import PersonIcon from "@mui/icons-material/Person";
import SettingsIcon from "@mui/icons-material/Settings";
import LogoutIcon from "@mui/icons-material/Logout";

import logo from "../../assets/logo.png";
import logoCompact from "../../assets/logo-compact.png";

const NavItem = ({ text, icon, path, onClick, open }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const isSelected = path ? location.pathname === path : false;

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (path) {
      navigate(path);
    }
  };

  return (
    <ListItem disablePadding sx={{ mb: 0.5, display: "block" }}>
      <ListItemButton
        selected={isSelected}
        onClick={handleClick}
        sx={{
          minHeight: 48,
          justifyContent: open ? "initial" : "center",
          px: 2.5,
          borderRadius: 0,
          color: "text.secondary",
          transition: "justify-content 0.2s",

          "&.Mui-selected": {
            bgcolor: "secondary.light",
            color: "primary.main",
            "&:hover": { bgcolor: "secondary.main" },
            "& .MuiListItemIcon-root": { color: "primary.main" },
          },
          "&:hover": {
            bgcolor: "action.hover",
            color: "primary.main",
            "& .MuiListItemIcon-root": { color: "primary.main" },
          },
        }}
      >
        <ListItemIcon
          sx={{
            minWidth: 0,
            mr: open ? 2 : "auto",
            justifyContent: "center",
            color: "inherit",
            transition: "margin 0.2s",
          }}
        >
          {icon}
        </ListItemIcon>

        <ListItemText
          primary={text}
          sx={{
            opacity: open ? 1 : 0,
            whiteSpace: "nowrap",
            transition: "opacity 0.2s ease-in-out",
            visibility: open ? "visible" : "hidden",
          }}
          slotProps={{
            primary: {
              fontSize: "0.95rem",
              fontWeight: isSelected ? 600 : 400,
            },
          }}
        />
      </ListItemButton>
    </ListItem>
  );
};

const Sidebar = ({ handleLogout, open }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isOpen = isMobile ? true : open;

  const MENU_ITEMS = [
    {
      text: "Dashboard",
      icon: <TimelineIcon fontSize="small" />,
      path: "/home",
    },
    {
      text: "Transactions",
      icon: <PaymentIcon fontSize="small" />,
      path: "/transactions",
    },
    {
      text: "Budget",
      icon: <PieChartIcon fontSize="small" />,
      path: "/budget",
    },
    {
      text: "AI Assistant",
      icon: <AssistantIcon fontSize="small" />,
      path: "/ai-assistant",
    },
  ];

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

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        bgcolor: "background.paper",
        overflowX: "hidden",
      }}
    >
      {/* Logo */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
          minHeight: 64,
          position: "relative",
        }}
      >
        {/* Full Logo */}
        <Box
          component="img"
          src={logo}
          alt="Logo"
          sx={{
            height: 32,
            width: "auto",
            position: "absolute",
            left: 24,
            opacity: isOpen ? 1 : 0,
            transition: isOpen
              ? "opacity 0.3s ease-in-out 0.1s"
              : "opacity 0.1s ease-in-out",
          }}
        />

        {/* Compact Logo  */}
        <Box
          component="img"
          src={logoCompact}
          alt="Logo Compact"
          sx={{
            height: 32,
            width: "auto",
            position: "absolute",
            opacity: isOpen ? 0 : 1,
            transition: isOpen
              ? "opacity 0.1s ease-in-out"
              : "opacity 0.3s ease-in-out 0.1s",
          }}
        />
      </Box>

      {/* Menu Items */}
      <Box sx={{ flexGrow: 1, overflowY: "auto", overflowX: "hidden", mt: 1 }}>
        <List>
          {MENU_ITEMS.map((item) => (
            <NavItem key={item.text} {...item} open={isOpen} />
          ))}
        </List>
      </Box>

      {/* Promo Box */}
      {!isMobile && (
        <Box
          sx={{
            pb: 2,
            px: 2,
            opacity: isOpen ? 1 : 0,
            transition: "opacity 0.3s ease",
            pointerEvents: isOpen ? "auto" : "none",
          }}
        >
          <Box sx={{ bgcolor: "grey.200", p: 2, borderRadius: 2 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ whiteSpace: "nowrap" }}
            >
              Promo / Upgrade
            </Typography>
          </Box>
        </Box>
      )}

      {/* Mobile Settings Section */}
      {isMobile && (
        <Box
          sx={{
            pb: 2,
            paddingBottom: "calc(16px + env(safe-area-inset-bottom))",
          }}
        >
          <Divider sx={{ my: 2 }} />
          <Box sx={{ px: 3, mb: 1 }}>
            <Typography
              variant="caption"
              fontWeight="bold"
              color="text.disabled"
            >
              ACCOUNT
            </Typography>
          </Box>
          <List>
            {SETTINGS_ITEMS.map((item) => (
              <NavItem key={item.text} {...item} open={isOpen} />
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default Sidebar;
