import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import TimelineIcon from "@mui/icons-material/Timeline";
import PeopleIcon from "@mui/icons-material/People";
import PieChartIcon from "@mui/icons-material/PieChart";
import SettingsIcon from "@mui/icons-material/Settings";
import logo from "../assets/logo1.png";
import { useLocation, useNavigate } from "react-router-dom";

const menuItems = [
  { text: "Dashboard", icon: <TimelineIcon />, path: "/home" },
  { text: "Transactions", icon: <PeopleIcon />, path: "/transactions" },
  { text: "Budget", icon: <PieChartIcon />, path: "/budget" },
];

const NavItem = ({ text, icon, path, onClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const isSelected = path ? location.pathname === path : false;

  return (
    <ListItem disablePadding>
      <ListItemButton
        selected={isSelected}
        onClick={onClick || (() => navigate(path))}
        sx={{
          mx: 1.5,
          mb: 1,
          borderRadius: 2,
          "&.Mui-selected": {
            backgroundColor: "secondary.light",
            color: "primary.main",
            "&:hover": { backgroundColor: "secondary.light" },
            "& .MuiListItemIcon-root": { color: "primary.main" },
          },
          "&:hover": { backgroundColor: "action.hover" },
        }}
      >
        <ListItemIcon sx={{ minWidth: 40, color: "inherit" }}>
          {icon}
        </ListItemIcon>
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  );
};

const Sidebar = () => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
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
          sx={{ height: 48, width: "auto" }}
        />
      </Box>
      <Divider sx={{ mb: 2 }} />
      {/* Menu Items */}
      <Box sx={{ flexGrow: 1, overflowY: "auto" }}>
        <List>
          {menuItems.map((item) => (
            <NavItem key={item.text} {...item} />
          ))}
        </List>
      </Box>

      <Box sx={{ p: 2, textAlign: "center" }}>
        <Box sx={{ bgcolor: "grey.200", p: 2, borderRadius: 2 }}>
          Promo Image
        </Box>
      </Box>

      <Divider sx={{ my: 1 }} />

      <Box>
        <NavItem text="Settings" icon={<SettingsIcon />} path="/settings" />
      </Box>
    </Box>
  );
};

export default Sidebar;
