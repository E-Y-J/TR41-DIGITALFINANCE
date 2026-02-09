import { useState, useEffect, useRef } from "react";
import { Box, IconButton, Divider, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

import MessageList from "./components/MessageList";
import ChatInput from "./components/ChatInput";
import { useAxios } from "../../hooks/useAxios";
import { sendChatMessage } from "../../api/user";

const ChatBubble = ({ handleChatDrawerToggle, user }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const apiClient = useAxios();

  useEffect(() => {
    return () => {
      setMessages([]);
      setInputValue("");
      setIsTyping(false);
    };
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: userMessage, sender: user?.nickname || "User" },
    ]);
    setInputValue("");
    setIsTyping(true);

    try {
      // Call the real backend AI API
      const response = await sendChatMessage(apiClient, userMessage, {});
      const aiResponse = response?.data?.response || "I received your message.";

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: aiResponse,
          sender: "ai",
        },
      ]);
    } catch (error) {
      console.error("Chat API error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: "Sorry, I couldn't process your message. Please try again.",
          sender: "ai",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
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
