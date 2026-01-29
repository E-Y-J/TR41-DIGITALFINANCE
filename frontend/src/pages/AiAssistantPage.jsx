import { useState, useRef, useEffect } from "react";
import { Box, Paper, Typography, Button, Drawer, alpha } from "@mui/material";

import HistoryIcon from "@mui/icons-material/History";

import ChatSidebar from "../features/chat/components/ChatSidebar";
import MessageList from "../features/chat/components/MessageList";
import ChatInput from "../features/chat/components/ChatInput";

const MOCK_HISTORY = [
  {
    id: 1,
    title: "Budget Planning 2026",
    date: "Today",
    messages: [
      { id: 101, sender: "user", text: "Help me plan my budget" },
      { id: 102, sender: "ai", text: "Sure! Lets start with your income." },
    ],
  },
];

const AiAssistantPage = () => {
  const [conversations, setConversations] = useState(MOCK_HISTORY);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);

  const messagesEndRef = useRef(null);

  const handleSelectChat = (id) => {
    setActiveChatId(id);
    const selected = conversations.find((c) => c.id === id);
    setMessages(selected ? selected.messages : []);
  };

  const handleNewChat = () => {
    setActiveChatId(null);
    setMessages([]);
  };

  const handleSendMessage = (text = inputValue) => {
    if (!text.trim()) return;

    const newUserMsg = { id: Date.now(), text: text, sender: "user" };
    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue("");
    setIsTyping(true);

    setTimeout(() => {
      const newAiMsg = {
        id: Date.now() + 1,
        text: "I am analyzing your financial data...",
        sender: "ai",
      };
      setMessages((prev) => [...prev, newAiMsg]);
      setIsTyping(false);

      if (!activeChatId) {
        const newChatId = Date.now();
        const newConversation = {
          id: newChatId,
          title: text.slice(0, 30) + "...",
          date: "Just now",
          messages: [newUserMsg, newAiMsg],
        };
        setConversations((prev) => [newConversation, ...prev]);
        setActiveChatId(newChatId);
      }
    }, 1500);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <Box
      sx={{
        display: "flex",
        height: "calc(100vh - 110px)",
        width: "100%",
        bgcolor: "#F8FAFC",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <Drawer
        anchor="bottom"
        open={mobileHistoryOpen}
        onClose={() => setMobileHistoryOpen(false)}
        slotProps={{
          paper: {
            sx: {
              borderTopLeftRadius: 24,
              borderTopRightRadius: 24,
              maxHeight: "70vh",
              bgcolor: "#F8FAFC",
              backgroundImage: "none",
              boxShadow: "0 -4px 20px rgba(0,0,0,0.08)",
            },
          },
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 4,
            bgcolor: "grey.400",
            borderRadius: 10,
            mx: "auto",
            mt: 1.5,
            mb: 1,
            opacity: 0.6,
          }}
        />

        <ChatSidebar
          isMobile={true}
          conversations={conversations}
          activeChatId={activeChatId}
          onSelectChat={(id) => {
            handleSelectChat(id);
            setMobileHistoryOpen(false);
          }}
          onNewChat={() => {
            handleNewChat();
            setMobileHistoryOpen(false);
          }}
        />
      </Drawer>

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          height: "100%",
          minWidth: 0,
        }}
      >
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
            onClick={() => setMobileHistoryOpen(true)}
            sx={{
              textTransform: "none",
              fontWeight: 700,
              color: "text.secondary",
              bgcolor: alpha("#fff", 0.5),
              backdropFilter: "blur(4px)",
              borderRadius: 2,
              px: 1.5,
              border: "1px solid",
              borderColor: "divider",
              "&:hover": { bgcolor: alpha("#fff", 0.8) },
            }}
          >
            History
          </Button>
        </Box>

        <Box sx={{ flexGrow: 1, overflowY: "auto" }}>
          <MessageList
            messages={messages}
            isTyping={isTyping}
            messagesEndRef={messagesEndRef}
            onSuggestionClick={(text) => handleSendMessage(text)}
          />
        </Box>

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
              onSend={() => handleSendMessage()}
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
      </Box>

      <Box
        sx={{
          display: { xs: "none", md: "block" },
          height: "100%",
          flexShrink: 0,
        }}
      >
        <ChatSidebar
          conversations={conversations}
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
        />
      </Box>
    </Box>
  );
};

export default AiAssistantPage;
