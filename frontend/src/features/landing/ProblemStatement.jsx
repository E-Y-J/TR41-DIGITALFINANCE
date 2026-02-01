import { Box, Typography, Container, Stack } from "@mui/material";
import AuthButton from "../../features/auth/AuthButton";

const ProblemStatement = () => {
  return (
    <Box
      id="about"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.paper",
        py: { xs: 8, md: 0 },
      }}
    >
      <Container maxWidth="md">
        <Stack spacing={4} alignItems="center" textAlign="center">
          <Typography
            variant="overline"
            sx={{
              color: "primary.main",
              fontWeight: 800,
              letterSpacing: 2,
              bgcolor: "secondary.light",
              px: 2,
              py: 0.5,
              borderRadius: 1,
            }}
          >
            The Problem
          </Typography>

          <Typography variant="h3" fontWeight={800} sx={{ lineHeight: 1.2 }}>
            Tired of scattered records and manual bookkeeping?
          </Typography>

          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ maxWidth: 700, lineHeight: 1.7, fontWeight: 400 }}
          >
            Users struggle with inconsistent tracking across multiple e-wallets.
            This leads to poor financial awareness and prevents effective
            budgeting.
            <strong> Our AI-assisted tracker</strong> reduces manual work and
            centralizes everything for better decision-making.
          </Typography>
          <AuthButton
            mode="signup"
            size="large"
            sx={{
              px: 6,
              py: 2,
              fontSize: "1.1rem",
              borderRadius: 3,
            }}
          >
            Ready to get started?
          </AuthButton>
        </Stack>
      </Container>
    </Box>
  );
};

export default ProblemStatement;
