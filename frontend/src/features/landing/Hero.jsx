import { Box, Typography, Container, Stack } from "@mui/material";
import Grid from "@mui/material/Grid";
import AuthButton from "../auth/AuthButton";
import PreviewBox from "../../components/PreviewBox";
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
                <Box component="span" sx={{ color: "#1E88E5" }}>
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
            {/* Preview panel mirrored from FeaturesGrid (slightly larger on md+) */}
            <Box
              sx={{
                width: "100%",
                height: { xs: "auto", md: 550 }, // auto on mobile prevents cropping
                borderRadius: 4,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                boxShadow: "0 20px 50px rgba(2, 6, 23, 0.08)",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                position: "relative",
                p: { xs: 1.5, md: 3 },
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
                  src={dashboardImg}
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
