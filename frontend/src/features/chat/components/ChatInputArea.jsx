import { Box, Paper, Typography } from "@mui/material";
import ChatInput from "./ChatInput";

const ChatInputArea = ({ inputValue, setInputValue, onSend }) => (
  <Box
    sx={{
      p: { xs: 2, sm: 3 },
      pt: 1,
      maxWidth: 900,
      mx: "auto",
      width: "100%",
      flexShrink: 0,
    }}
  >
    <Paper
      elevation={0}
      sx={{
        borderRadius: 4,
        border: "1px solid",
        borderColor: "divider",
        bgcolor: "#ffffff",
        overflow: "hidden",
        boxShadow: "0 4px 12px rgba(0,0,0,0.03)",
      }}
    >
      <ChatInput
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSend={onSend}
        noBorder={true}
      />
    </Paper>
    <Typography
      variant="caption"
      color="text.secondary"
      align="center"
      sx={{ display: "block", mt: 1, opacity: 0.7 }}
    >
      AI can make mistakes. Verify important financial data.
    </Typography>
  </Box>
);

export default ChatInputArea;
