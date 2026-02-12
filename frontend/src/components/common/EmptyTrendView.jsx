import TimelineIcon from "@mui/icons-material/Timeline";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import { Box, Typography } from "@mui/material";

const EmptyTrendView = ({ header, text }) => {
  return (
    <Box
      sx={{
        height: 400,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: 6,
        border: "1px solid",
        borderColor: "divider",
        textAlign: "center",
        px: 3,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          position: "absolute",
          top: -20,
          right: -20,
          opacity: 0.03,
          transform: "rotate(15deg)",
        }}
      >
        <TimelineIcon sx={{ fontSize: 280 }} />
      </Box>

      <Box
        sx={{
          mb: 3,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: 80,
          height: 80,
          borderRadius: "24px",
          bgcolor: "primary.main",
          color: "white",
          boxShadow: 3,
        }}
      >
        <CalendarMonthIcon sx={{ fontSize: 40 }} />
      </Box>

      <Typography variant="h6" fontWeight={800} gutterBottom>
        {header}
      </Typography>

      <Typography
        color="text.secondary"
        variant="body1"
        sx={{ maxWidth: 300, mb: 3, lineHeight: 1.6 }}
      >
        {text}
      </Typography>

      <Typography
        variant="caption"
        sx={{
          color: "primary.main",
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: 1.5,
        }}
      >
        Use the filters above to begin
      </Typography>
    </Box>
  );
};

export default EmptyTrendView;
