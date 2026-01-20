import { Box, TextField, IconButton } from "@mui/material";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import SendIcon from "@mui/icons-material/Send";

const ChatInput = ({ inputValue, setInputValue, onSend }) => {
  return (
    <Box
      sx={{
        p: 2,
        borderTop: "1px solid",
        borderColor: "divider",
        paddingBottom: "calc(16px + env(safe-area-inset-bottom))",
      }}
    >
      <Box
        sx={{
          p: 1.25,
          borderRadius: 3,
          border: "1px solid",
          borderColor: "divider",
          boxShadow: 1,
          transition: "box-shadow 0.2s, border-color 0.2s",
          "&:focus-within": { borderColor: "primary.main" },
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="How can I help you?"
          variant="standard"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          slotProps={{ input: { disableUnderline: true } }}
          sx={{
            "& .MuiInputBase-root": { fontSize: "0.95rem" },
            "& textarea": { resize: "none", scrollbarGutter: "stable" },
          }}
        />

        <Box
          sx={{
            mt: 1,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <IconButton color="primary" component="label" size="small">
            <AttachFileIcon fontSize="small" />
            <input hidden type="file" multiple />
          </IconButton>
          <IconButton
            color="primary"
            size="small"
            onClick={onSend}
            disabled={!inputValue.trim()}
          >
            <SendIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInput;
