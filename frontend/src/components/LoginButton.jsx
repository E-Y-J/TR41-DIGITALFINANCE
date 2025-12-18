import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "@mui/material";

const LoginButton = () => {
  const { loginWithRedirect } = useAuth0();

  const handleLogin = async () => {
    await loginWithRedirect({
      appState: {
        returnTo: "/home",
      },
    });
  };

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={handleLogin}
      sx={{ width: "100px" }}
    >
      Log In
    </Button>
  );
};

export default LoginButton;
