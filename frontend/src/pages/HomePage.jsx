import DashboardIcon from "@mui/icons-material/Dashboard";
import { Stack, Button, Typography } from "@mui/material";
import LogoutButton from "../components/LogoutButton";
import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";

const HomePage = () => {
  const { getAccessTokenSilently } = useAuth0();
  useEffect(() => {
    async function fetchToken() {
      const token = await getAccessTokenSilently();
      console.log("Access Token:", token);
    }
    fetchToken();
  });

  return (
    <Stack spacing={2} direction="column" alignItems="center" sx={{ mt: 10 }}>
      <DashboardIcon color="primary" sx={{ fontSize: 60 }} />

      <Typography variant="h4" component="h1">
        This is the Homepage that needs to be protected
      </Typography>

      <Button variant="contained" onClick={() => alert("It works!")}>
        Click Me
      </Button>
      <LogoutButton />
    </Stack>
  );
};

export default HomePage;
