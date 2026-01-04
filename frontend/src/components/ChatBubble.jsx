import {
  Box,
  IconButton,
  TextField,
  InputAdornment,
  Typography,
  Stack,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import SendIcon from "@mui/icons-material/Send";

const ChatBubble = ({ handleChatDrawerToggle }) => {
  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
      }}
    >
      {/* 1. Header Area  */}
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{
          p: { xs: 1.5, sm: 2 },
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Typography variant="subtitle1" fontWeight="bold">
          Assistant (Some title?)
        </Typography>
        <IconButton onClick={handleChatDrawerToggle} size="small">
          <CloseIcon />
        </IconButton>
      </Stack>

      {/* 2. Chat History Area */}
      <Box sx={{ flexGrow: 1, overflowY: "auto", p: 2 }}>
        {/* Chat messages will render here */}
      </Box>

      {/* 3. Input Area  */}
      <Box
        sx={{
          p: { xs: 1, sm: 2 },
          borderTop: "1px solid",
          borderColor: "divider",
          paddingBottom: "calc(8px + env(safe-area-inset-bottom))",
          bgcolor: "background.paper",
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="How can I help you?"
          variant="outlined"
          size="small"
          slotProps={{
            input: {
              endAdornment: (
                <InputAdornment
                  position="end"
                  sx={{ alignSelf: "flex-end", mb: 0.5 }}
                >
                  <IconButton
                    color="primary"
                    size="small"
                    edge="end"
                    onClick={() => console.log("Send!")}
                  >
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
          sx={{
            "& .MuiInputBase-root": {
              fontSize: "0.9rem",
              pr: 1,
            },
          }}
          // can add styling to the scroll bar
        />
      </Box>
    </Box>
  );
};

export default ChatBubble;
