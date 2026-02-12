import { Box, Typography, Container, Stack, Divider } from "@mui/material";
import Grid from "@mui/material/Grid";
import AppNavLink from "../../components/common/AppNavLink";

const NAV_LINKS = [
  { text: "Home", path: "#hero" },
  { text: "Features", path: "#features" },
  { text: "Our Mission", path: "#about" },
];

const LEGAL_LINKS = [
  { text: "Privacy", path: "/privacy" },
  { text: "Terms", path: "/terms" },
  { text: "Security", path: "/security" },
];

const RESOURCE_LINKS = [
  { text: "Docs", path: "/docs" },
  { text: "API Reference", path: "/api" },
  { text: "Guides", path: "/guides" },
];

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: { xs: 4, md: 5 },
        bgcolor: "background.paper",
        borderTop: "1px solid",
        borderColor: "divider",
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={{ xs: 3, md: 2 }} alignItems="flex-start">
          <Grid size={{ xs: 12, md: 3 }} sx={{ mb: { xs: 3, md: 0 } }}>
            <Box
              component="img"
              src="/logo.png"
              alt="SecureBank AI Logo"
              sx={{
                height: 24,
                width: "auto",
                mb: 1.5,
                bgcolor: "white",
                borderRadius: 1,
                p: 0.5,
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: "block", maxWidth: 220, lineHeight: 1.5 }}
            >
              AI-assisted finance tracking for your unified dashboard.
            </Typography>
          </Grid>

          <Grid container size={{ xs: 12, md: 9 }} spacing={{ xs: 2, md: 0 }}>
            {[
              { label: "Product", links: NAV_LINKS },
              { label: "Resources", links: RESOURCE_LINKS },
              { label: "Legal", links: LEGAL_LINKS },
            ].map((section) => (
              <Grid key={section.label} size={{ xs: 4 }}>
                <Typography
                  variant="overline"
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                    display: "block",
                    color: "text.primary",
                  }}
                >
                  {section.label}
                </Typography>
                <Stack spacing={0.5}>
                  {section.links.map((link) => (
                    <AppNavLink
                      key={link.text}
                      text={link.text}
                      path={link.path}
                      sx={{
                        p: 0,
                        minHeight: "auto",
                        fontSize: "0.8rem",
                        justifyContent: "flex-start",
                        bgcolor: "transparent",
                        "&:hover": {
                          bgcolor: "transparent",
                          color: "primary.main",
                        },
                      }}
                    />
                  ))}
                </Stack>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Divider sx={{ my: 3 }} />
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            justifyContent: "space-between",
            alignItems: "center",
            gap: 1,
          }}
        >
          <Typography
            variant="caption"
            color="text.disabled"
            sx={{ fontSize: "0.7rem" }}
          >
            © {new Date().getFullYear()} SecureBank AI.
          </Typography>
          <Typography
            variant="caption"
            color="text.disabled"
            sx={{ fontSize: "0.7rem", fontStyle: "italic" }}
          >
            Empowering your financial visibility.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
