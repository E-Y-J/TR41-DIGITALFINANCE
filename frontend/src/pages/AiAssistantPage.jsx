import { useState, useRef, useEffect } from "react";
import { Box } from "@mui/material";

import MobileChatHeader from "../features/chat/components/MobileChatHeader";
import ChatInputArea from "../features/chat/components/ChatInputArea";
import ChatHistoryDrawer from "../features/chat/components/ChatHistoryDrawer";

import ChatSidebar from "../features/chat/components/ChatSidebar";
import MessageList from "../features/chat/components/MessageList";

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

export default function AiAssistantPage() {
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
      <ChatHistoryDrawer
        open={mobileHistoryOpen}
        onClose={() => setMobileHistoryOpen(false)}
        sidebarProps={{
          conversations,
          activeChatId,
          onSelectChat: (id) => {
            handleSelectChat(id);
            setMobileHistoryOpen(false);
          },
          onNewChat: () => {
            handleNewChat();
            setMobileHistoryOpen(false);
          },
        }}
      />

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          height: "100%",
          minWidth: 0,
        }}
      >
        <MobileChatHeader onOpenHistory={() => setMobileHistoryOpen(true)} />

        <Box sx={{ flexGrow: 1, overflowY: "auto" }}>
          <MessageList
            messages={messages}
            isTyping={isTyping}
            messagesEndRef={messagesEndRef}
            onSuggestionClick={handleSendMessage}
          />
        </Box>

        <ChatInputArea
          inputValue={inputValue}
          setInputValue={setInputValue}
          onSend={() => handleSendMessage()}
        />
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
}
