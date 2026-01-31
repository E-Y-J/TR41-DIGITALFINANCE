import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "@mui/material";

const AuthButton = ({
  mode = "login",
  children,
  sx = {},
  variant,
  ...props
}) => {
  const { loginWithRedirect } = useAuth0();

  const handleAuth = async () => {
    const options = {
      appState: { returnTo: "/home" },
    };

    if (mode === "signup") {
      options.authorizationParams = { screen_hint: "signup" };
    }
    await loginWithRedirect(options);
  };

  const isSignup = mode === "signup";

  const defaultStyles = {
    borderRadius: 2,
    textTransform: "none",
    fontWeight: 600,
    py: 1.2,
    ...(isSignup
      ? {
          bgcolor: "primary.main",
          boxShadow: "0 4px 14px 0 rgba(30, 136, 225, 0.39)",
          "&:hover": {
            bgcolor: "primary.light",
            boxShadow: "0 6px 20px 0 rgba(30, 136, 225, 0.45)",
          },
        }
      : {
          borderColor: "primary.main",
          color: "primary.main",
        }),
    ...sx,
  };

  return (
    <Button
      onClick={handleAuth}
      variant={variant || (isSignup ? "contained" : "outlined")}
      sx={defaultStyles}
      {...props}
    >
      {children || (isSignup ? "Sign Up" : "Log In")}
    </Button>
  );
};

export default AuthButton;
