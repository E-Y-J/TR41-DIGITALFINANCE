import { useState, useEffect, useRef } from "react";
import { Box, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

const ChatBubble = ({ handleChatDrawerToggle }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add User Message
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: inputValue, sender: "user" },
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
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 1.25,
          display: "flex",
          alignItems: "center",
          justifyContent: "flex-end",
        }}
      >
        <IconButton onClick={handleChatDrawerToggle} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Message List */}
      <Box sx={{ flexGrow: 1, overflowY: "auto", p: 1.75 }}>
        <MessageList
          messages={messages}
          isTyping={isTyping}
          messagesEndRef={messagesEndRef}
        />
      </Box>

      {/* Input Area */}
      <ChatInput
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSend={handleSendMessage}
      />
    </Box>
  );
};

export default ChatBubble;
