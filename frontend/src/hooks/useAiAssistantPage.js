import { useState, useRef, useMemo, useCallback } from "react";
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

  const [mockedSessions, setMockedSessions] = useState([]);

  const messagesEndRef = useRef(null);

  const conversations = useMemo(() => {
    const serverHistory = (sessionHistory || []).map((session) => ({
      id: session.id,
      title:
        session.conversation_history?.[0]?.content.slice(0, 30) ||
        "Recent Chat",
      isMock: false,
      messages: (session.conversation_history || []).map((msg, idx) => ({
        id: `${session.id}-${idx}`,
        text: msg.content,
        sender: msg.role === "assistant" ? "ai" : "user",
      })),
    }));

    return [...mockedSessions, ...serverHistory];
  }, [sessionHistory, mockedSessions]);

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

  const suggestionClickHandler = useCallback(
    (text) => {
      setInputValue(text);
    },
    [setInputValue],
  );

  const handleSendMessage = async (textOverride) => {
    const messageText = (
      typeof textOverride === "string" ? textOverride : inputValue
    ).trim();

    if (!messageText) return;

    setInputValue("");
    setIsTyping(true);
    if (!activeChatId) {
      const newMockId = `mock-${Date.now()}`;
      const newMockSession = {
        id: newMockId,
        title: messageText.slice(0, 30),
        isMock: true,
        messages: [{ id: Date.now(), text: messageText, sender: "user" }],
      };

      setMockedSessions((prev) => [newMockSession, ...prev]);
      setActiveChatId(newMockId);

      setTimeout(() => {
        setMockedSessions((prev) =>
          prev.map((s) =>
            s.id === newMockId
              ? {
                  ...s,
                  messages: [
                    ...s.messages,
                    {
                      id: Date.now() + 1,
                      text: "I'm a mock AI response for this new chat!",
                      sender: "ai",
                    },
                  ],
                }
              : s,
          ),
        );
        setIsTyping(false);
      }, 1500);
    } else {
      const newUserMsg = { id: Date.now(), text: messageText, sender: "user" };
      setOptimisticMessages((prev) => [...prev, newUserMsg]);

      setTimeout(() => {
        const newAiMsg = {
          id: Date.now() + 1,
          text: "I am analyzing your follow-up request...",
          sender: "ai",
        };

        if (activeChatId.toString().startsWith("mock")) {
          setMockedSessions((prev) =>
            prev.map((s) =>
              s.id === activeChatId
                ? { ...s, messages: [...s.messages, newUserMsg, newAiMsg] }
                : s,
            ),
          );
          setOptimisticMessages([]);
        } else {
          setOptimisticMessages((prev) => [...prev, newAiMsg]);
        }

        setIsTyping(false);
      }, 1500);
    }
  };

  return {
    user: userData,
    isLoading,
    conversations,
    activeChatId,
    displayMessages,
    suggestionClickHandler,
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
