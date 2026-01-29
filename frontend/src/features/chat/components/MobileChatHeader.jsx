import { Box, Button, alpha } from "@mui/material";
import HistoryIcon from "@mui/icons-material/History";

const MobileChatHeader = ({ onOpenHistory }) => {
  return (
    <Box
      sx={{
        display: { xs: "flex", md: "none" },
        alignItems: "center",
        justifyContent: "flex-end",
        px: 2,
        py: 1,
        bgcolor: "transparent",
        zIndex: 1,
      }}
    >
      <Button
        size="small"
        startIcon={<HistoryIcon sx={{ fontSize: 18 }} />}
        onClick={onOpenHistory}
        sx={{
          textTransform: "none",
          fontWeight: 700,
          borderRadius: 2,
          px: 2,
          minWidth: "fit-content",
          color: "text.secondary",
          border: "1px solid",
          borderColor: "divider",
          bgcolor: alpha("#fff", 0.6),
          backdropFilter: "blur(4px)",

          "&:hover": {
            bgcolor: "action.hover",
            borderColor: "grey.400",
          },
        }}
      >
        History
      </Button>
    </Box>
  );
};

export default MobileChatHeader;
