import { useState, useRef, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useGetChatHistory } from "../features/chat/useGetChatHistory";
import { useGetUser } from "../features/auth/useGetUser";
import { useAxios } from "./useAxios";
import { sendChatMessage } from "../api/user";

export const useAiAssistantPage = () => {
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  // sessionHistory now reflects the { sessions: [...] } structure
  const { data: historyResponse, isLoading } = useGetChatHistory();
  const { data: userData } = useGetUser();

  const [activeChatId, setActiveChatId] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);
  const [localSessions, setLocalSessions] = useState([]);

  const messagesEndRef = useRef(null);

  const conversations = useMemo(() => {
    // 1. Access the sessions array from the new response structure
    const rawSessions = historyResponse?.sessions || [];

    const serverHistory = rawSessions.map((session) => ({
      id: session.id,
      // Use the first user message for the title, or fallback
      title:
        session.conversation_history
          ?.find((m) => m.role === "user")
          ?.content.slice(0, 30) || "Recent Chat",
      isMock: false,
      messages: (session.conversation_history || []).map((msg, idx) => ({
        id: `${session.id}-${idx}`,
        text: msg.content,
        sender: msg.role === "assistant" ? "ai" : "user",
      })),
      updatedAt: session.updated_at,
    }));

    // Combine local sessions with server history, avoiding duplicates
    const serverIds = new Set(serverHistory.map((s) => s.id));
    const uniqueLocal = localSessions.filter((s) => !serverIds.has(s.id));

    // Combine and sort by most recently updated
    return [...uniqueLocal, ...serverHistory].sort(
      (a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0),
    );
  }, [historyResponse, localSessions]);

  const activeSession = useMemo(
    () => conversations.find((c) => c.id === activeChatId),
    [activeChatId, conversations],
  );

  const displayMessages = useMemo(() => {
    const history = activeSession?.messages || [];

    // Only show optimistic messages if they aren't already in the server history
    const filteredOptimistic = optimisticMessages.filter(
      (opt) => !history.some((h) => h.text === opt.text),
    );

    return [...history, ...filteredOptimistic];
  }, [activeSession, optimisticMessages]);

  const handleSendMessage = async (textOverride) => {
    const messageText = (
      typeof textOverride === "string" ? textOverride : inputValue
    ).trim();

    if (!messageText) return;

    setInputValue("");
    setIsTyping(true);

    // Add user message optimistically
    const userMsgId = Date.now();
    const newUserMsg = { id: userMsgId, text: messageText, sender: "user" };

    if (!activeChatId) {
      // New chat - create a local session first
      const newSessionId = `local-${Date.now()}`;
      const newSession = {
        id: newSessionId,
        title: messageText.slice(0, 30),
        isMock: true,
        messages: [newUserMsg],
        updatedAt: new Date().toISOString(),
      };

      setLocalSessions((prev) => [newSession, ...prev]);
      setActiveChatId(newSessionId);
    } else {
      // Existing chat - add optimistic message
      setOptimisticMessages((prev) => [...prev, newUserMsg]);
    }

    try {
      // Call the actual backend API
      // Pass sessionId to continue the conversation in that specific session
      const response = await sendChatMessage(apiClient, messageText, {
        sessionId: activeChatId?.startsWith("local-") ? null : activeChatId,
      });

      const aiResponse = response?.data?.response || "I received your message but couldn't generate a response.";
      const aiMsgId = Date.now() + 1;
      const newAiMsg = { id: aiMsgId, text: aiResponse, sender: "ai" };

      // Update local session or optimistic messages with AI response
      if (activeChatId?.startsWith("local-")) {
        setLocalSessions((prev) =>
          prev.map((s) =>
            s.id === activeChatId
              ? {
                  ...s,
                  messages: [...s.messages, newAiMsg],
                  updatedAt: new Date().toISOString(),
                }
              : s,
          ),
        );
      } else {
        setOptimisticMessages((prev) => [...prev, newAiMsg]);
      }

      // Refresh chat history from server after a short delay
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["chatHistory"] });
      }, 1000);

    } catch (error) {
      console.error("Failed to send chat message:", error);

      // Add error message
      const errorMsg = {
        id: Date.now() + 1,
        text: "Sorry, I couldn't process your message. Please try again.",
        sender: "ai",
      };

      if (activeChatId?.startsWith("local-")) {
        setLocalSessions((prev) =>
          prev.map((s) =>
            s.id === activeChatId
              ? {
                  ...s,
                  messages: [...s.messages, errorMsg],
                  updatedAt: new Date().toISOString(),
                }
              : s,
          ),
        );
      } else {
        setOptimisticMessages((prev) => [...prev, errorMsg]);
      }
    } finally {
      setIsTyping(false);
    }
  };

  return {
    user: userData,
    isLoading,
    conversations,
    activeChatId,
    displayMessages,
    suggestionClickHandler: handleSendMessage,
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
