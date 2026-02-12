import { memo, useEffect, useMemo } from "react";
import {
  Box,
  Stack,
  Typography,
  Avatar,
  Paper,
  keyframes,
} from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import MessageEmptyState from "./MessageEmptyState";
import Typewriter from "./Typewriter";
import FormattedMessage from "../../../components/common/FormattedMessage";
import ActionButtons, {
  ACTION_PRESETS,
} from "../../../components/common/ActionButtons";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const bounce = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
`;

/**
 * Detect if a message requires user confirmation
 * Returns the type of confirmation needed or null if none
 */
const detectConfirmationType = (text) => {
  if (!text) return null;

  const lowerText = text.toLowerCase();

  // Check for explicit confirmation patterns
  if (
    lowerText.includes("confirm?") ||
    lowerText.includes("(yes/no)") ||
    lowerText.includes("yes or no")
  ) {
    // Check if it's a transaction-related confirmation
    if (
      lowerText.includes("add") ||
      lowerText.includes("expense") ||
      lowerText.includes("income") ||
      lowerText.includes("transaction")
    ) {
      return "CONFIRM_WITH_EDIT";
    }
    return "CONFIRM";
  }

  // Check for other confirmation patterns
  if (
    lowerText.includes("would you like") ||
    lowerText.includes("should i") ||
    lowerText.includes("do you want")
  ) {
    return "CONFIRM";
  }

  return null;
};

/**
 * Remove the confirmation prompt text from the message for cleaner display
 */
const cleanConfirmationText = (text) => {
  if (!text) return text;
  // Remove "(yes/no)" pattern but keep "Confirm?"
  return text.replace(/\s*\(yes\/no\)\s*/gi, " ").trim();
};

const TypingIndicator = () => (
  <Box sx={{ display: "flex", gap: 0.5, ml: 2, mb: 2 }}>
    {[0, 1, 2].map((i) => (
      <Box
        key={i}
        sx={{
          width: 6,
          height: 6,
          bgcolor: "primary.light",
          borderRadius: "50%",
          animation: `${bounce} 1s infinite ease-in-out`,
          animationDelay: `${i * 0.2}s`,
        }}
      />
    ))}
  </Box>
);

const MessageItem = memo(
  ({ msg, isAI, isLast, onActionClick, showActions }) => {
    // Detect if this message needs confirmation buttons
    const confirmationType = useMemo(
      () => (isAI && showActions ? detectConfirmationType(msg.text) : null),
      [msg.text, isAI, showActions],
    );

    // Get the appropriate action preset
    const actions = useMemo(() => {
      if (!confirmationType) return null;
      return ACTION_PRESETS[confirmationType] || ACTION_PRESETS.CONFIRM;
    }, [confirmationType]);

    // Clean the message text for display
    const displayText = useMemo(
      () => (confirmationType ? cleanConfirmationText(msg.text) : msg.text),
      [msg.text, confirmationType],
    );

    const handleAction = (value) => {
      onActionClick?.(value);
    };

    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: isAI ? "flex-start" : "flex-end",
          animation: `${fadeIn} 0.3s ease-out`,
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            gap: 1,
            maxWidth: "85%",
            flexDirection: isAI ? "row" : "row-reverse",
          }}
        >
          {isAI && (
            <Avatar
              sx={{
                width: 28,
                height: 28,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: "divider",
                mt: 0.5,
              }}
            >
              <SmartToyIcon sx={{ fontSize: 16, color: "primary.main" }} />
            </Avatar>
          )}

          <Box sx={{ display: "flex", flexDirection: "column" }}>
            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                borderRadius: isAI
                  ? "16px 16px 16px 4px"
                  : "16px 16px 4px 16px",
                bgcolor: isAI ? "background.paper" : "primary.main",
                color: isAI ? "text.primary" : "primary.contrastText",
                border: "1px solid",
                borderColor: isAI ? "divider" : "transparent",
              }}
            >
              {isAI ? (
                isLast ? (
                  <Typewriter text={displayText} speed={15} />
                ) : (
                  <FormattedMessage text={displayText} />
                )
              ) : (
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    lineHeight: 1.5,
                    fontSize: { xs: "0.9rem", sm: "0.875rem" },
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    overflowWrap: "anywhere",
                  }}
                >
                  {msg.text}
                </Typography>
              )}
            </Paper>

            {actions && (
              <ActionButtons
                actions={actions}
                onAction={handleAction}
                show={showActions}
                size="small"
              />
            )}
          </Box>
        </Box>
      </Box>
    );
  },
);

export const MessageList = ({
  messages,
  isTyping,
  messagesEndRef,
  onSuggestionClick,
  user,
  onSendMessage,
}) => {
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }, 100);
    return () => clearTimeout(timeoutId);
  }, [messages, isTyping, messagesEndRef]);

  // Handler for action button clicks
  const handleActionClick = (value) => {
    // Send the response as a message
    if (onSendMessage) {
      onSendMessage(value);
    } else if (onSuggestionClick) {
      onSuggestionClick(value);
    }
  };

  if (messages.length === 0) {
    return (
      <MessageEmptyState onSuggestionClick={onSuggestionClick} user={user} />
    );
  }

  return (
    <Stack spacing={2.5} sx={{ p: 2, pb: 8 }}>
      {messages.map((msg, index) => {
        const isLast = index === messages.length - 1;
        const isAI = msg.sender === "ai";
        // Only show actions on the last AI message when not typing
        const showActions = isAI && isLast && !isTyping;

        return (
          <MessageItem
            key={msg.id || index}
            msg={msg}
            isAI={isAI}
            isLast={isLast}
            showActions={showActions}
            onActionClick={handleActionClick}
          />
        );
      })}

      {isTyping && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </Stack>
  );
};

export default MessageList;
