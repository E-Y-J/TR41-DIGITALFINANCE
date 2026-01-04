import React from "react";
import { Box, Button, TextField } from "@mui/material";

const ChatBubble = ({ handleChatDrawerToggle }) => {
  return (
    <Box sx={{ p: 2, width: 300 }}>
      <Button variant="contained" onClick={handleChatDrawerToggle}>
        Close Chat
      </Button>
      <Box sx={{ mt: 2 }}>
        <TextField id="outlined-basic" label="Outlined" variant="outlined" />
      </Box>
    </Box>
  );
};

export default ChatBubble;
