import { useState, useRef, useMemo } from "react";
import { useGetChatHistory } from "../features/chat/useGetChatHistory";
import { useGetUser } from "../features/auth/useGetUser";

export const useAiAssistantPage = () => {
  const { data: sessionHistory, isLoading } = useGetChatHistory();
  const { data: userData } = useGetUser();

  const [activeChatId, setActiveChatId] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);

  const messagesEndRef = useRef(null);

  const conversations = useMemo(() => {
    return (sessionHistory || []).map((session) => ({
      id: session.id,
      title:
        session.conversation_history?.[0]?.content.slice(0, 30) || "New Chat",
      messages: (session.conversation_history || []).map((msg, idx) => ({
        id: `${session.id}-${idx}`,
        text: msg.content,
        sender: msg.role === "assistant" ? "ai" : "user",
      })),
    }));
  }, [sessionHistory]);

  const activeSession = conversations.find((c) => c.id === activeChatId);

  const displayMessages = useMemo(() => {
    const history = activeSession?.messages || [];

    return [
      ...history,
      ...optimisticMessages.filter(
        (opt) => !history.some((h) => h.text === opt.text),
      ),
    ];
  }, [activeSession, optimisticMessages]);

  const handleSendMessage = async (text = inputValue) => {
    const msg = text.trim();
    if (!msg) return;

    setOptimisticMessages((prev) => [
      ...prev,
      { id: Date.now(), text: msg, sender: "user" },
    ]);
    setInputValue("");
    setIsTyping(true);

    setTimeout(() => {
      setOptimisticMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, text: "Analyzing data...", sender: "ai" },
      ]);
      setIsTyping(false);
    }, 1500);
  };

  return {
    user: userData,
    isLoading,
    conversations,
    activeChatId,
    displayMessages,
    inputValue,
    setInputValue,
    isTyping,
    mobileHistoryOpen,
    setMobileHistoryOpen,
    messagesEndRef,
    handleSendMessage,
    handleSelectChat: (id) => {
      setActiveChatId(id);
      setOptimisticMessages([]);
    },
    handleNewChat: () => {
      setActiveChatId(null);
      setOptimisticMessages([]);
    },
  };
};
