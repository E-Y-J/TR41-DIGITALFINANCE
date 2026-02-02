import { Box, Typography, Avatar } from "@mui/material";
import SearchOffIcon from "@mui/icons-material/SearchOff";

const EmptyState = ({ header, text }) => {
  return (
    <Box
      sx={{
        width: "100%",
        py: 8,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        bgcolor: "background.paper",
      }}
    >
      <Avatar sx={{ bgcolor: "grey.100", width: 56, height: 56, mb: 2 }}>
        <SearchOffIcon sx={{ color: "text.secondary" }} />
      </Avatar>
      <Typography variant="h6" color="text.primary" gutterBottom>
        {header}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 300 }}>
        {text}
      </Typography>
    </Box>
  );
};

export default EmptyState;
