import { Box, Typography, Container, Stack } from "@mui/material";
import Grid from "@mui/material/Grid";
import AuthButton from "../auth/AuthButton";
import PreviewImage from "../../components/PreviewImage";
import dashboardImg from "../../assets/dashboard.png";

const Hero = () => {
  return (
    <Box
      id="hero"
      component="section"
      sx={{
        minHeight: { xs: "auto", md: "100vh" },
        display: "flex",
        alignItems: "center",
        bgcolor: "background.default",
        pt: { xs: 12, md: 0 },
        pb: { xs: 8, md: 0 },
        overflow: "hidden",
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={{ xs: 6, md: 4 }} alignItems="center">
          <Grid size={{ xs: 12, md: 6 }}>
            <Stack spacing={3}>
              <Typography
                variant="overline"
                sx={{
                  color: "primary.main",
                  fontWeight: 800,
                  letterSpacing: 2,
                  display: "block",
                }}
              >
                Smart Finance Management
              </Typography>

              <Typography
                variant="h1"
                sx={{
                  fontWeight: 900,
                  fontSize: { xs: "2.8rem", md: "4rem" },
                  lineHeight: 1.1,
                  color: "text.primary",
                }}
              >
                Digital <br />
                <Box component="span" sx={{ color: "primary.main" }}>
                  Finance
                </Box>
              </Typography>

              <Typography
                variant="h6"
                sx={{
                  color: "text.secondary",
                  fontWeight: 400,
                  maxWidth: 480,
                  lineHeight: 1.6,
                }}
              >
                Centralize your income, expenses, and e-wallets. Utilize
                AI-powered insights to master your spending patterns.
              </Typography>

              <Stack direction={{ xs: "column", sm: "row" }} spacing={2} pt={1}>
                <AuthButton mode="signup" size="large" sx={{ px: 4, py: 1.8 }}>
                  Start Tracking Free
                </AuthButton>
                <AuthButton
                  mode="login"
                  variant="outlined"
                  size="large"
                  sx={{ px: 4, py: 1.8 }}
                >
                  View Demo
                </AuthButton>
              </Stack>
            </Stack>
          </Grid>

          <Grid size={{ xs: 12, md: 6 }}>
            {/* Dashboard Preview Panel */}
            <Box
              sx={{
                width: "100%",
                height: { xs: "auto", md: 450 },
                borderRadius: 4,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                boxShadow: "0 25px 50px -12px rgba(0,0,0,0.15)",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                p: 2,
              }}
            >
              <PreviewImage
                src={dashboardImg}
                alt="Dashboard Preview"
                fit="contain"
              />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Hero;
