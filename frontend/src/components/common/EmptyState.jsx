import { Box, Typography, Avatar, alpha, useTheme } from "@mui/material";
import SearchOffIcon from "@mui/icons-material/SearchOff";

const EmptyState = ({ header, text }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  return (
    <Box
      sx={{
        width: "100%",
        py: 10,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        bgcolor: "transparent",
      }}
    >
      <Avatar
        sx={{
          bgcolor: isDarkMode
            ? alpha(theme.palette.primary.main, 0.15)
            : "grey.100",
          width: 64,
          height: 64,
          mb: 3,
          border: isDarkMode
            ? `1px solid ${alpha(theme.palette.primary.main, 0.2)}`
            : "none",
        }}
      >
        <SearchOffIcon
          sx={{
            fontSize: 32,
            color: isDarkMode ? "primary.main" : "text.secondary",
          }}
        />
      </Avatar>

      <Typography
        variant="h6"
        fontWeight={700}
        color="text.primary"
        gutterBottom
      >
        {header}
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{
          maxWidth: 320,
          lineHeight: 1.6,
          opacity: 0.8,
        }}
      >
        {text}
      </Typography>
    </Box>
  );
};

export default EmptyState;
