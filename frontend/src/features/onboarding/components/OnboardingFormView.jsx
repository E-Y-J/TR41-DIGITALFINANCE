import { Box, Button, Alert, Fade } from "@mui/material";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import OnboardingTextField from "./OnboardingTextField";
import FormHeader from "./Formheader";

const OnboardingFormView = ({
  formData,
  handleChange,
  handleSubmit,
  isSubmitted,
  isPending,
  isError,
  error,
}) => {
  const textFieldStyles = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 3,
      backgroundColor: "#fff",
      transition: "all 0.2s ease-in-out",
      "&:hover": { backgroundColor: "#f9f9f9" },
      "&.Mui-focused": {
        backgroundColor: "#fff",
        boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
      },
    },
  };

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <FormHeader />

        {isError && (
          <Alert severity="error" sx={{ borderRadius: 3 }}>
            {error?.message || "Something went wrong."}
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
            <OnboardingTextField
              label="First Name"
              name="firstName"
              value={formData.firstName}
              error={isSubmitted && !formData.firstName}
              onChange={handleChange}
              styles={textFieldStyles}
            />
            <OnboardingTextField
              label="Last Name"
              name="lastName"
              value={formData.lastName}
              error={isSubmitted && !formData.lastName}
              onChange={handleChange}
              styles={textFieldStyles}
            />
          </Box>

          <OnboardingTextField
            label="Nickname"
            name="nickName"
            value={formData.nickName}
            error={isSubmitted && !formData.nickName}
            onChange={handleChange}
            styles={textFieldStyles}
          />

          <OnboardingTextField
            label="Annual Salary"
            name="annualSalary"
            type="number"
            value={formData.annualSalary}
            error={isSubmitted && !formData.annualSalary}
            helperText={
              !formData.annualSalary
                ? "Required"
                : "Used to tailor your budget plan."
            }
            onChange={handleChange}
            styles={textFieldStyles}
            startAdornment={
              <AttachMoneyIcon fontSize="small" color="primary" />
            }
          />

          <Button
            disabled={isPending}
            type="submit"
            variant="contained"
            size="large"
            sx={{
              mt: 2,
              py: 1.8,
              borderRadius: 4,
              textTransform: "none",
              fontWeight: 700,
              background: "linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)",
              "&:hover": { transform: "translateY(-1px)" },
            }}
          >
            {isPending ? "Setting up..." : "Complete Setup"}
          </Button>
        </Box>
      </Box>
    </Fade>
  );
};

export default OnboardingFormView;
