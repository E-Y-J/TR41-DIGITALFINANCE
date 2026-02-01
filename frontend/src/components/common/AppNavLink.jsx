import {
  Button,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const AppNavLink = ({
  text,
  icon,
  path,
  onClick,
  open = true,
  isSidebar = false,
  sx = {},
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  const isSelected = path
    ? location.pathname === path || location.hash === path
    : false;

  const handleClick = (e) => {
    if (path?.startsWith("#")) {
      e.preventDefault();

      const targetId = path.replace("#", "");
      const elem = document.getElementById(targetId);

      if (elem) {
        elem.scrollIntoView({ behavior: "smooth" });
        if (onClick) onClick(e);
      }
    } else if (onClick) {
      onClick(e);
    } else if (path) {
      navigate(path);
    }
  };

  const sharedStyles = {
    minHeight: 48,
    px: 2.5,
    borderRadius: isSidebar ? 0 : 1,
    color: isSelected ? "primary.main" : "text.secondary",
    bgcolor: isSelected ? "secondary.light" : "transparent",
    transition: "all 0.2s ease-in-out",

    "&.Mui-selected": {
      bgcolor: "secondary.light",
      color: "primary.main",
      "&:hover": { bgcolor: "secondary.main" },
    },
    "&:hover": {
      bgcolor: isSelected ? "secondary.main" : "action.hover",
      color: "primary.main",
      "& .MuiListItemIcon-root": { color: "primary.main" },
    },
    ...sx,
  };

  if (isSidebar) {
    return (
      <ListItemButton
        selected={isSelected}
        onClick={handleClick}
        sx={sharedStyles}
      >
        {icon && (
          <ListItemIcon
            sx={{ minWidth: 0, mr: open ? 2 : "auto", color: "inherit" }}
          >
            {icon}
          </ListItemIcon>
        )}
        <ListItemText
          primary={text}
          sx={{ opacity: open ? 1 : 0, whiteSpace: "nowrap" }}
          slotProps={{
            primary: {
              fontSize: "0.95rem",
              fontWeight: isSelected ? 600 : 400,
            },
          }}
        />
      </ListItemButton>
    );
  }

  return (
    <Button
      onClick={handleClick}
      sx={{ ...sharedStyles, textTransform: "none" }}
    >
      {text}
    </Button>
  );
};

export default AppNavLink;
