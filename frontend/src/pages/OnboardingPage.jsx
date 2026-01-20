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
  InputAdornment,
  Fade,
} from "@mui/material";
import LogoutButton from "../components/LogoutButton";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import { useUpdateUser } from "../hooks/queries/useUpdateUser";
import PageLoader from "../components/PageLoader";

const OnboardingForm = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { mutate, isPending, isError } = useUpdateUser();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    nickName: "",
    annualSalary: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);

    if (
      !formData.firstName ||
      !formData.lastName ||
      !formData.nickName ||
      !formData.annualSalary
    ) {
      return;
    }

    mutate({
      first_name: formData.firstName,
      last_name: formData.lastName,
      nick_name: formData.nickName,
      annual_salary: formData.annualSalary,
      account_status: "active",
    });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: (theme) =>
          `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.primary.light}20 100%)`,
      }}
    >
      <Container maxWidth="sm">
        <Fade in={true} timeout={800}>
          <Paper
            elevation={2}
            sx={{
              p: { xs: 3, md: 5 },
              display: "flex",
              flexDirection: "column",
              gap: 4,
              borderRadius: 6,
              backgroundColor: "rgba(255, 255, 255, 0.8)",
              backdropFilter: "blur(20px)",
            }}
          >
            <LogoutButton />
            <Box textAlign="center">
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 800,
                  mb: 1,
                  background:
                    "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Welcome
              </Typography>
              <Typography
                variant="body1"
                color="text.secondary"
                sx={{ fontWeight: 500 }}
              >
                Let's get your profile set up in seconds.
              </Typography>
            </Box>

            {isError && (
              <Alert
                severity="error"
                sx={{ borderRadius: 3, border: "1px solid #ffcdd2" }}
              >
                {isError?.message || "Something went wrong."}
              </Alert>
            )}

            <Box
              component="form"
              onSubmit={handleSubmit}
              noValidate
              sx={{ display: "flex", flexDirection: "column", gap: 3 }}
            >
              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  flexDirection: { xs: "column", sm: "row" },
                }}
              >
                <TextField
                  error={isSubmitted && !formData.firstName}
                  helperText={
                    isSubmitted && !formData.firstName ? "Required" : ""
                  }
                  label="First Name"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  fullWidth
                  variant="outlined"
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: 3,
                      backgroundColor: "#fff",
                      "&:hover": { backgroundColor: "#f9f9f9" },
                      "&.Mui-focused": {
                        backgroundColor: "#fff",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                      },
                    },
                  }}
                />

                <TextField
                  error={isSubmitted && !formData.lastName}
                  helperText={
                    isSubmitted && !formData.lastName ? "Required" : ""
                  }
                  label="Last Name"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  fullWidth
                  variant="outlined"
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: 3,
                      backgroundColor: "#fff",
                      "&:hover": { backgroundColor: "#f9f9f9" },
                      "&.Mui-focused": {
                        backgroundColor: "#fff",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                      },
                    },
                  }}
                />
              </Box>
              <TextField
                error={isSubmitted && !formData.nickName}
                helperText={isSubmitted && !formData.nickName ? "Required" : ""}
                label="Nickname"
                name="nickName"
                value={formData.nickName}
                onChange={handleChange}
                required
                fullWidth
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 3,
                    backgroundColor: "#fff",
                    "&:hover": { backgroundColor: "#f9f9f9" },
                    "&.Mui-focused": {
                      backgroundColor: "#fff",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                    },
                  },
                }}
              />
              <TextField
                error={isSubmitted && !formData.annualSalary}
                label="Annual Salary"
                name="annualSalary"
                value={formData.annualSalary}
                onChange={handleChange}
                helperText={
                  isSubmitted && !formData.annualSalary
                    ? "Salary is required"
                    : "Used to tailor your budget plan."
                }
                type="number"
                onKeyDown={(e) =>
                  ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()
                }
                fullWidth
                variant="outlined"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 3,
                    backgroundColor: "#fff",
                    "&:hover": { backgroundColor: "#f9f9f9" },
                    "&.Mui-focused": {
                      backgroundColor: "#fff",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                    },
                  },
                }}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <AttachMoneyIcon
                          fontSize="small"
                          sx={{ color: "primary.main" }}
                        />
                      </InputAdornment>
                    ),
                  },
                }}
              />

              <Button
                disabled={isPending}
                type="submit"
                variant="contained"
                size="large"
                sx={{
                  mt: 1,
                  py: 1.5,
                  borderRadius: 3,
                  textTransform: "none",
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  boxShadow: 4,
                  background:
                    "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                  transition: "transform 0.2s",
                  "&:hover": {
                    transform: "scale(1.02)",
                    boxShadow: "0 6px 20px 0 rgba(33, 150, 243, 0.60)",
                  },
                }}
              >
                {isPending ? "Setting up..." : "Complete Setup"}
              </Button>
            </Box>
          </Paper>
        </Fade>

        <Backdrop
          sx={{
            color: "#fff",
            zIndex: (theme) => theme.zIndex.drawer + 999,
            backgroundColor: "rgba(255, 255, 255, 0.5)",
            backdropFilter: "blur(5px)",
          }}
          open={isPending}
        >
          <PageLoader />
        </Backdrop>
      </Container>
    </Box>
  );
};

export default OnboardingForm;
