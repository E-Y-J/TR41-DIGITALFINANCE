import { useState } from "react";
import { Box, Container, Paper, Backdrop } from "@mui/material";
import { useUpdateUser } from "../features/onboarding/useUpdateUser";
import PageLoader from "../components/common/PageLoader";
import OnboardingFormView from "../features/onboarding/components/OnboardingFormView";

export default function OnboardingPage() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    nickName: "",
    annualSalary: "",
  });
  const { mutate, isPending, isError, isSuccess, error } = useUpdateUser();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);
    if (Object.values(formData).some((val) => !val)) return;

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
        bgcolor: "#F8FAFC",
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 4, md: 6 },
            borderRadius: 6,
            border: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
            boxShadow: "0 24px 48px rgba(0,0,0,0.04)",
          }}
        >
          <OnboardingFormView
            formData={formData}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
            isSubmitted={isSubmitted}
            isPending={isPending}
            isError={isError}
            error={error}
          />
        </Paper>

        <Backdrop
          sx={{
            color: "#fff",
            zIndex: 1201,
            bgcolor: "rgba(255, 255, 255, 0.6)",
            backdropFilter: "blur(4px)",
          }}
          open={isPending || isSuccess}
        >
          <PageLoader />
        </Backdrop>
      </Container>
    </Box>
  );
}
