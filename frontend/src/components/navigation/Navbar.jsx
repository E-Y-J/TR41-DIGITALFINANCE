import { useNavigate } from "react-router-dom";
import { AppBar, Toolbar, Box, Button, Stack } from "@mui/material";
import AuthButton from "../AuthButton";
import logo from "../../assets/logo1.png";

const Navbar = () => {
  const navigate = useNavigate();

  const NAV_LINKS = [
    { title: "Features", id: "features" },
    { title: "About Us", id: "about_us" },
    { title: "Pricing", id: "pricing" },
  ];

  // to be implemented: smooth scroll to section
  const handleScroll = (id) => {
    console.log(id);
    return;
  };

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        width: "100%",
        bgcolor: "background.paper",
        color: "text.primary",
        borderBottom: "1px solid",
        borderColor: "divider",
      }}
    >
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        {/* Logo */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
          }}
        >
          <Box
            component="img"
            src={logo}
            alt="Logo"
            sx={{ height: 40, width: "auto" }}
          />
        </Box>

        {/* Navigation Links */}
        <Box
          sx={{
            flexGrow: 1,
            display: { xs: "none", md: "flex" },
            justifyContent: "center",
            gap: 3,
          }}
        >
          {NAV_LINKS.map((link) => (
            <Button
              key={link.title}
              color="inherit"
              onClick={() => handleScroll(link.id)}
              sx={{ fontWeight: 500 }}
            >
              {link.title}
            </Button>
          ))}
        </Box>

        {/* Auth Buttons */}
        <Stack direction="row" spacing={2}>
          <AuthButton mode="login" color="inherit" variant="text">
            Log In
          </AuthButton>

          <AuthButton
            mode="signup"
            variant="contained"
            color="primary"
            sx={{ boxShadow: "none" }}
          >
            Sign Up
          </AuthButton>
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
