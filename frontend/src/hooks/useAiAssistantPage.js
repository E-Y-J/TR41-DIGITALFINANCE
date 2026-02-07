import { useState, useRef, useMemo, useCallback } from "react";
import { useGetChatHistory } from "../features/chat/useGetChatHistory";
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
  const { mutateAsync: sendChatApi } = useSendChatMessage();

  const [activeChatId, setActiveChatId] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);

  const messagesEndRef = useRef(null);

  const conversations = useMemo(() => {
    const rawSessions = historyResponse?.sessions || [];
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
        })),
        updatedAt: session.updated_at,
      }))
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  }, [historyResponse]);

  const activeSession = useMemo(
    () => conversations.find((c) => c.id === activeChatId),
    [activeChatId, conversations],
  );

  const suggestionClickHandler = useCallback(
    (text) => {
      setInputValue(text);
    },
    [setInputValue],
  );

  const displayMessages = useMemo(() => {
    const history = activeSession?.messages || [];

    if (history.length === 0 && optimisticMessages.length > 0) {
      return optimisticMessages;
    }

    return [...history, ...optimisticMessages];
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
    setOptimisticMessages([userMsg]);

    try {
      const result = await sendChatApi({
        message: messageText,
        context: activeChatId ? { session_id: activeChatId } : {},
      });

      const aiMsg = {
        id: `ai-${Date.now()}`,
        text: result.response,
        sender: "ai",
        intent: result.intent,
        parsedData: result.parsed_data,
      };

      setOptimisticMessages([userMsg, aiMsg]);
      const sessionId = result.session_id || result.data?.session_id;
      if (sessionId) {
        setActiveChatId(sessionId);
      }

      await refetchHistory();
      setOptimisticMessages([]);
    } catch (error) {
      console.log(error);
      setOptimisticMessages((prev) => [
        ...prev,
        {
          id: "err",
          text: "Connection lost. Please try again.",
          sender: "ai",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

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
    suggestionClickHandler,
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
