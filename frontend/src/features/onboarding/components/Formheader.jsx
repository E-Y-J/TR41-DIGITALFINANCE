import { Box, Typography } from "@mui/material";

const FormHeader = () => (
  <Box textAlign="center">
    <Typography
      variant="h4"
      sx={{
        fontWeight: 800,
        mb: 1,
        letterSpacing: "-0.5px",
        background: "linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
      }}
    >
      Welcome
    </Typography>
    <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
      Let's get your profile set up in seconds.
    </Typography>
  </Box>
);

export default FormHeader;
