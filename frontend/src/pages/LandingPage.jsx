import Button from "@mui/material/Button";
import DashboardIcon from "@mui/icons-material/Dashboard";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import LoginButton from "../components/LoginButton.jsx";

export default function LandingPage() {
  return (
    <Stack spacing={2} direction="column" alignItems="center" sx={{ mt: 10 }}>
      <DashboardIcon color="primary" sx={{ fontSize: 60 }} />

      <Typography variant="h4" component="h1">
        MUI is Active
      </Typography>

      <Button variant="contained" onClick={() => alert("It works!")}>
        Click Me
      </Button>
      <LoginButton />
    </Stack>
  );
}
