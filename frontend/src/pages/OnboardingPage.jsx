import { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Container,
  Paper,
  Alert,
  Backdrop,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useUpdateUser } from "../hooks/queries/useUpdateUser";
import PageLoader from "../components/PageLoader";

const OnboardingForm = () => {
  const { mutate, isPending, isError } = useUpdateUser();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
  });
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    mutate(
      {
        first_name: formData.firstName,
        last_name: formData.lastName,
        account_status: "active",
      },
      {
        onSuccess: () => {
          navigate("/home");
        },
      }
    );
  };

  return (
    <Container maxWidth="sm">
      <Paper
        elevation={3}
        sx={{ p: 4, mt: 8, display: "flex", flexDirection: "column", gap: 3 }}
      >
        <Box textAlign="center">
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Please complete your profile to continue to the dashboard.
          </Typography>
        </Box>

        {isError && <Alert severity="error">{isError}</Alert>}

        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <TextField
            label="First Name"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            required
            fullWidth
            variant="outlined"
          />

          <TextField
            label="Last Name"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            required
            fullWidth
            variant="outlined"
          />

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isPending}
            sx={{ mt: 2 }}
          >
            {isPending ? "Saving..." : "Complete Setup"}
          </Button>
        </Box>
      </Paper>
      <Backdrop
        sx={{
          color: "#fff",
          zIndex: (theme) => theme.zIndex.drawer + 999,
          backgroundColor: "rgba(255, 255, 255, 0.8)",
        }}
        open={isPending}
      >
        <PageLoader />
      </Backdrop>
    </Container>
  );
};

export default OnboardingForm;
