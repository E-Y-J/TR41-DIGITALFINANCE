import { useState } from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Stack,
  Container,
  Divider,
  IconButton,
  Drawer,
  List,
} from "@mui/material";
import AppNavLink from "../components/common/AppNavLink";
import AuthButton from "../features/auth/AuthButton";

import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";

const NAV_LINKS = [
  { text: "Home", path: "#hero" },
  { text: "Our Mission", path: "#about" },
  { text: "Features", path: "#features" },
];

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
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
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: "space-between" }}>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Box
              component="img"
              src="/logo.png"
              alt="SecureBank AI Logo"
              sx={{
                height: 32,
                width: "auto",
                bgcolor: "white",
                borderRadius: 1,
                p: 0.5,
              }}
            />
          </Box>

          <Box sx={{ display: { xs: "none", md: "flex" }, gap: 1 }}>
            {NAV_LINKS.map((link) => (
              <AppNavLink key={link.text} text={link.text} path={link.path} />
            ))}
          </Box>

          <Stack
            direction="row"
            spacing={2}
            sx={{ display: { xs: "none", md: "flex" } }}
          >
            <AuthButton
              mode="login"
              variant="text"
              sx={{ color: "text.primary" }}
            >
              Log In
            </AuthButton>
            <AuthButton
              mode="signup"
              variant="contained"
              sx={{
                bgcolor: "primary.main",
                boxShadow: "none",
                "&:hover": { bgcolor: "primary.light", boxShadow: "none" },
              }}
            >
              Get Started
            </AuthButton>
          </Stack>

          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </Container>

      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        slotProps={{
          paper: {
            sx: {
              width: 280,
              bgcolor: "background.paper",
              backgroundImage: "none",
              borderLeft: "1px solid",
              borderColor: "divider",
              display: "flex",
              flexDirection: "column",
            },
          },
        }}
      >
        <Box
          sx={{
            p: 1.5,
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
          }}
        >
          <IconButton onClick={handleDrawerToggle} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider sx={{ mx: 2, opacity: 0.6 }} />

        <Box sx={{ flexGrow: 1, py: 2 }}>
          <List sx={{ px: 1.5 }}>
            {NAV_LINKS.map((link) => (
              <AppNavLink
                key={link.text}
                text={link.text}
                path={link.path}
                isSidebar={true}
                onClick={handleDrawerToggle}
                sx={{
                  borderRadius: 2,
                  mb: 1,
                  "& .MuiTypography-root": {
                    fontSize: "1.1rem",
                    fontWeight: 500,
                  },
                }}
              />
            ))}
          </List>
        </Box>

        <Box
          sx={{
            p: 3,
            borderTop: "1px solid",
            borderColor: "divider",
          }}
        >
          <Stack spacing={2}>
            <AuthButton mode="login" fullWidth />
            <AuthButton mode="signup" fullWidth />
          </Stack>
        </Box>
      </Drawer>
    </AppBar>
  );
};

export default Navbar;
