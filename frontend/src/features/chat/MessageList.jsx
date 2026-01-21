import {
  Box,
  Stack,
  Typography,
  Avatar,
  Paper,
  keyframes,
} from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import Typewriter from "./Typewriter";

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
`;

const MessageList = ({ messages, isTyping, messagesEndRef }) => {
  // View A: Empty State
  if (messages.length === 0) {
    return (
      <Box
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          opacity: 0.8,
        }}
      >
        <Avatar sx={{ width: 64, height: 64, bgcolor: "primary.light", mb: 2 }}>
          <SmartToyIcon sx={{ fontSize: 32, color: "primary.main" }} />
        </Avatar>
        <Typography variant="h6" gutterBottom>
          How can I help you today?
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ maxWidth: 250 }}
        >
          Ask me about your dashboard, recent analytics, or general settings.
        </Typography>
      </Box>
    );
  }

  // View B: Message History
  return (
    <Stack spacing={2}>
      {messages.map((msg) => (
        <Box
          key={msg.id}
          sx={{
            display: "flex",
            justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
          }}
        >
          {msg.sender === "ai" && (
            <Avatar
              sx={{ width: 32, height: 32, mr: 1, bgcolor: "primary.main" }}
            >
              <SmartToyIcon sx={{ fontSize: 20 }} />
            </Avatar>
          )}
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              maxWidth: "75%",
              borderRadius: 3,
              bgcolor: msg.sender === "user" ? "primary.main" : "grey.100",
              color: msg.sender === "user" ? "white" : "text.primary",
              borderTopRightRadius: msg.sender === "user" ? 0 : 12,
              borderTopLeftRadius: msg.sender === "ai" ? 0 : 12,
            }}
          >
            {msg.sender === "user" ? (
              <Typography variant="body2">{msg.text}</Typography>
            ) : (
              <Typewriter text={msg.text} />
            )}
          </Paper>
        </Box>
      ))}

      {isTyping && (
        <Box sx={{ display: "flex", gap: 0.5, ml: 5 }}>
          {[0, 1, 2].map((i) => (
            <Box
              key={i}
              sx={{
                width: 6,
                height: 6,
                bgcolor: "text.secondary",
                borderRadius: "50%",
                animation: `${bounce} 1.4s infinite ease-in-out both`,
                animationDelay: `${i * 0.16}s`,
              }}
            />
          ))}
        </Box>
      )}
      <div ref={messagesEndRef} />
    </Stack>
  );
};

export default MessageList;
