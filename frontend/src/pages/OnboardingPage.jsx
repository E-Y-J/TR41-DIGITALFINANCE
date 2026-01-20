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
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import { useUpdateUser } from "../hooks/queries/useUpdateUser";
import PageLoader from "../components/PageLoader";

const OnboardingForm = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { mutate, isPending, isError, isSuccess, error } = useUpdateUser();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    nickName: "",
    annualSalary: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);

    const { firstName, lastName, nickName, annualSalary } = formData;

    if (!firstName || !lastName || !nickName || !annualSalary) {
      return;
    }

    mutate({
      first_name: firstName,
      last_name: lastName,
      nick_name: nickName,
      annual_salary: annualSalary,
      account_status: "active",
    });
  };

  // Reusable style object
  const textFieldStyles = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: "#fff",
      "&:hover": { backgroundColor: "#f9f9f9" },
      "&.Mui-focused": {
        backgroundColor: "#fff",
        boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
      },
    },
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
                {error?.message || "Something went wrong."}
              </Alert>
            )}

            <Box
              component="form"
              onSubmit={handleSubmit}
              noValidate
              sx={{ display: "flex", flexDirection: "column", gap: 3 }}
            >
              {/* Name Row */}
              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  flexDirection: { xs: "column", sm: "row" },
                }}
              >
                <TextField
                  label="First Name"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  error={isSubmitted && !formData.firstName}
                  helperText={
                    isSubmitted && !formData.firstName ? "Required" : ""
                  }
                  required
                  fullWidth
                  variant="outlined"
                  sx={textFieldStyles}
                />
                <TextField
                  label="Last Name"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  error={isSubmitted && !formData.lastName}
                  helperText={
                    isSubmitted && !formData.lastName ? "Required" : ""
                  }
                  required
                  fullWidth
                  variant="outlined"
                  sx={textFieldStyles}
                />
              </Box>

              <TextField
                label="Nickname"
                name="nickName"
                value={formData.nickName}
                onChange={handleChange}
                error={isSubmitted && !formData.nickName}
                helperText={isSubmitted && !formData.nickName ? "Required" : ""}
                required
                fullWidth
                variant="outlined"
                sx={textFieldStyles}
              />

              <TextField
                label="Annual Salary"
                name="annualSalary"
                value={formData.annualSalary}
                onChange={handleChange}
                error={isSubmitted && !formData.annualSalary}
                helperText={
                  !formData.annualSalary
                    ? "Salary is required"
                    : "Used to tailor your budget plan."
                }
                type="number"
                required
                fullWidth
                variant="outlined"
                sx={textFieldStyles}
                onKeyDown={(e) =>
                  ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()
                }
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
                disabled={isPending || isSuccess}
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
                    boxShadow: 6,
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
          open={isPending || isSuccess}
        >
          <PageLoader />
        </Backdrop>
      </Container>
    </Box>
  );
};

export default OnboardingForm;
