import {
  Box,
  Button,
  Typography,
  Container,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import HomeIcon from "@mui/icons-material/Home";

const NotFound = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const goHome = () => navigate("/home");
  const goBack = () => navigate(-1);

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100dvh",
          textAlign: "center",
          gap: { xs: 2, sm: 3 },
          px: 2,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: { xs: 80, sm: 120 },
            height: { xs: 80, sm: 120 },
            borderRadius: "50%",
            bgcolor: "error.lighter",
            color: "error.main",
          }}
        >
          <ErrorOutlineIcon sx={{ fontSize: { xs: 50, sm: 80 } }} />
        </Box>

        <Box>
          <Typography
            variant={isMobile ? "h2" : "h1"}
            fontWeight={800}
            color="text.primary"
          >
            404
          </Typography>
          <Typography
            variant={isMobile ? "h6" : "h5"}
            color="text.secondary"
            gutterBottom
          >
            Oops! Page not found.
          </Typography>
          <Typography
            variant="body2"
            color="text.disabled"
            sx={{ mb: 2, maxWidth: 300, mx: "auto" }}
          >
            The page you're looking for doesn't exist or has been moved.
          </Typography>
        </Box>

        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            gap: 2,
            width: { xs: "100%", sm: "auto" },
          }}
        >
          <Button
            variant="contained"
            size="large"
            startIcon={<HomeIcon />}
            onClick={goHome}
            sx={{ borderRadius: 2, px: 4, py: { xs: 1.5, sm: 1 } }}
          >
            Go Home
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={goBack}
            sx={{ borderRadius: 2, px: 4, py: { xs: 1.5, sm: 1 } }}
          >
            Go Back
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default NotFound;
