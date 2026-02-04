import { useState, useEffect, useRef } from "react";
import { Box, IconButton, Divider, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";

const ChatBubble = ({ handleChatDrawerToggle, user }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    return () => {
      setMessages([]);
      setInputValue("");
      setIsTyping(false);
    };
  }, []);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: inputValue, sender: user?.nickname || "User" },
    ]);
    setInputValue("");
    setIsTyping(true);

    // Simulate AI Response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: "This is a simulated AI response.",
          sender: "ai",
        },
      ]);
      setIsTyping(false);
    }, 3000);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          p: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "flex-end",
        }}
      >
        <IconButton onClick={handleChatDrawerToggle} size="small">
          <CloseIcon />
        </IconButton>
      </Box>
      <Divider />

      <Box
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          p: 2,
        }}
      >
        <MessageList
          messages={messages}
          isTyping={isTyping}
          messagesEndRef={messagesEndRef}
          onSuggestionClick={(text) => {
            setInputValue(text);
          }}
          user={user?.first_name ?? ""}
        />
      </Box>

      <Box sx={{ p: 1, pb: { xs: 2, sm: 1 } }}>
        <ChatInput
          inputValue={inputValue}
          setInputValue={setInputValue}
          onSend={handleSendMessage}
        />
      </Box>
    </Box>
  );
};

export default ChatBubble;
