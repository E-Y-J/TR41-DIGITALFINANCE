import { Box, Typography, Container, Stack } from "@mui/material";
import Grid from "@mui/material/Grid";
import AuthButton from "../auth/AuthButton";
import PreviewBox from "../../components/PreviewBox";
import PreviewImage from "../../components/PreviewImage";

const Hero = () => {
  return (
    <Box
      id="hero"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        bgcolor: "background.default",
        pt: { xs: 8, md: 0 },
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={{ xs: 6, md: 10 }} alignItems="center">
          <Grid item xs={12} md={6}>
            <Stack spacing={3}>
              <Typography
                variant="overline"
                sx={{
                  color: "primary.main",
                  fontWeight: 800,
                  letterSpacing: 1.5,
                }}
              >
                Smart Finance Management
              </Typography>

              <Typography
                variant="h1"
                sx={{
                  fontWeight: 900,
                  fontSize: { xs: "3rem", md: "4.5rem" },
                  lineHeight: 1.1,
                  letterSpacing: -1,
                  color: "text.primary",
                }}
              >
                Digital <br />
                <span style={{ color: "#1E88E5" }}>Finance</span>
              </Typography>

              <Typography
                variant="h6"
                sx={{
                  color: "text.secondary",
                  fontWeight: 400,
                  maxWidth: 500,
                  lineHeight: 1.6,
                }}
              >
                Centralize your income, expenses, and e-wallets. Utilize
                AI-powered insights and predictions to master your spending
                patterns.
              </Typography>

              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                sx={{ pt: 2 }}
              >
                <AuthButton
                  mode="signup"
                  size="large"
                  sx={{ px: 5, py: 1.5, fontSize: "1rem" }}
                >
                  Start Tracking Free
                </AuthButton>
                <AuthButton
                  mode="login"
                  variant="outlined"
                  size="large"
                  sx={{
                    px: 5,
                    py: 1.5,
                    fontSize: "1rem",
                    color: "text.primary",
                    borderColor: "divider",
                    "&:hover": { borderColor: "primary.main" },
                  }}
                >
                  View Demo
                </AuthButton>
              </Stack>
            </Stack>
          </Grid>

          <Grid item xs={12} md={6}>
            {/* Preview panel mirrored from FeaturesGrid (slightly larger on md+) */}
            <Box
              sx={{
                width: "100%",
                height: { xs: "auto", md: 550 }, // maintain original hero feel on md+
                borderRadius: 4,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
                boxShadow: "0 20px 50px rgba(2, 6, 23, 0.08)",
                p: { xs: 1.5, md: 3 },
                overflow: "hidden",
              }}
            >
              <PreviewBox
                label="Dashboard Preview"
                aspectRatio={{ xs: "16 / 9", md: "16 / 9" }}
                minHeight={{ xs: 240, md: 360 }}
                maxWidth="100%"
                sx={{ p: 0, width: "100%", height: "100%" }}
              >
                <PreviewImage
                  src="/trend.png" // MARK: 
                  // TODO: substitute with actual screenshot when available
                  alt="Dashboard preview"
                  fit="contain"
                />
              </PreviewBox>

              {/* Decorative glow */}
              <Box
                sx={{
                  position: "absolute",
                  bottom: -20,
                  left: -20,
                  width: 140,
                  height: 140,
                  bgcolor: "secondary.light",
                  borderRadius: "50%",
                  filter: "blur(80px)",
                  opacity: 0.3,
                  zIndex: -1,
                  pointerEvents: "none",
                }}
              />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Hero;
