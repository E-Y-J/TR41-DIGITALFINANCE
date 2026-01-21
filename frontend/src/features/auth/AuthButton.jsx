import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "@mui/material";

const AuthButton = ({ mode = "login", children, ...props }) => {
  const { loginWithRedirect } = useAuth0();

  const handleAuth = async () => {
    const options = {
      appState: {
        returnTo: "/home",
      },
    };

    if (mode === "signup") {
      options.authorizationParams = {
        screen_hint: "signup",
      };
    }

    await loginWithRedirect(options);
  };

  return (
    <Button onClick={handleAuth} {...props}>
      {children || (mode === "signup" ? "Sign Up" : "Log In")}
    </Button>
  );
};

export default AuthButton;
