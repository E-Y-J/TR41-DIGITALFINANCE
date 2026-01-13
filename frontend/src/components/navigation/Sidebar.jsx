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

import logo from "../../assets/logo1.png";

const NavItem = ({ text, icon, path, onClick }) => {
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
          mx: 1.5,
          borderRadius: 2,
          color: "text.secondary",

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
            mr: 2,
            justifyContent: "center",
            color: "inherit",
          }}
        >
          {icon}
        </ListItemIcon>
        <ListItemText
          primary={text}
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

const Sidebar = ({ handleLogout }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

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
        borderRight: "1px solid",
        borderColor: "divider",
      }}
    >
      {/* Logo Section */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          p: 1,
        }}
      >
        <Box
          component="img"
          src={logo}
          alt="Logo"
          sx={{ height: 40, width: "auto" }}
        />
      </Box>

      {/* Menu Items */}
      <Box sx={{ flexGrow: 1, overflowY: "auto", px: 0 }}>
        <List>
          {MENU_ITEMS.map((item) => (
            <NavItem key={item.text} {...item} />
          ))}
        </List>
      </Box>

      {!isMobile && (
        <Box sx={{ pb: 2, px: 2 }}>
          <Box sx={{ bgcolor: "grey.200", p: 2, borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Promo / Upgrade
            </Typography>
          </Box>
        </Box>
      )}

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
              sx={{ textTransform: "uppercase" }}
            >
              Account
            </Typography>
          </Box>
          <List>
            {SETTINGS_ITEMS.map((item) => (
              <NavItem key={item.text} {...item} />
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default Sidebar;
