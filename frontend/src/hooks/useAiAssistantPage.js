import { useState, useRef, useMemo, useCallback } from "react";
import {
  useGetChatHistory,
  useDeleteChatSession,
} from "../features/chat/useGetChatHistory";
import { useGetUser } from "../features/auth/useGetUser";
import { useSendChatMessage } from "../features/chat/useSendChatMessage";

export const useAiAssistantPage = () => {
  const {
    data: historyResponse,
    isLoading,
    isFetching,
    refetch: refetchHistory,
  } = useGetChatHistory();

  const { data: userData } = useGetUser();
  const deleteMutation = useDeleteChatSession();
  const { mutateAsync: sendChatApi } = useSendChatMessage();

  const [activeChatId, setActiveChatId] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);

  const messagesEndRef = useRef(null);

  const conversations = useMemo(() => {
    const rawSessions =
      historyResponse?.data?.sessions || historyResponse?.sessions || [];

    return rawSessions
      .map((session) => ({
        id: session.id,
        title:
          session.conversation_history
            ?.find((m) => m.role === "user")
            ?.content.slice(0, 30) || "Recent Chat",
        messages: (session.conversation_history || []).map((msg, idx) => ({
          id: `${session.id}-${idx}`,
          text: msg.content,
          sender: msg.role === "assistant" ? "ai" : "user",
          intent: msg.intent,
          parsedData: msg.parsed_data,
        })),
        updatedAt: session.updated_at,
      }))
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  }, [historyResponse]);

  const activeSession = useMemo(
    () => conversations.find((c) => c.id === activeChatId),
    [activeChatId, conversations],
  );

  const displayMessages = useMemo(() => {
    const history = activeSession?.messages || [];

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

    const userMsg = {
      id: `u-${Date.now()}`,
      text: messageText,
      sender: "user",
    };

    setOptimisticMessages((prev) => [...prev, userMsg]);

    try {
      const response = await sendChatApi({
        message: messageText,
        session_id: activeChatId,
      });

      const chatPayload = response.data?.data || response.data || response;
      const sessionId = chatPayload.session_id;

      const aiMsg = {
        id: `ai-${Date.now()}`,
        text: chatPayload.response,
        sender: "ai",
        intent: chatPayload.intent,
        parsedData: chatPayload.parsed_data,
        isOptimistic: true,
      };

      setOptimisticMessages((prev) => [...prev, aiMsg]);

      if (sessionId) {
        setActiveChatId(sessionId);
        await refetchHistory();
      }
    } catch (error) {
      console.error("Chat Error:", error);
      setOptimisticMessages((prev) => [
        ...prev,
        {
          id: "err",
          text: "Connection error. Please try again.",
          sender: "ai",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleTypewriterComplete = useCallback(() => {
    setOptimisticMessages([]);
  }, []);

  return {
    user: userData,
    isLoading,
    isFetching,
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
    handleTypewriterComplete,
    suggestionClickHandler: handleSendMessage,
    handleSelectChat: (id) => {
      setActiveChatId(id);
      setOptimisticMessages([]);
    },
    handleNewChat: () => {
      setActiveChatId(null);
      setOptimisticMessages([]);
    },
    handleDeleteChat: (chatId) => {
      // If it's a local-only session, just remove from local state
      if (chatId?.startsWith?.("local-")) {
        setLocalSessions((prev) => prev.filter((s) => s.id !== chatId));
      } else {
        // Delete from server
        deleteMutation.mutate(chatId);
      }
      // Clear active chat if we're deleting the active one
      if (activeChatId === chatId) {
        setActiveChatId(null);
        setOptimisticMessages([]);
      }
    },
    isDeletingChat: deleteMutation.isPending,
  };
};
