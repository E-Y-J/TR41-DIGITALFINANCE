import { memo, useEffect } from "react";
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
import { SpendingSummary, InsightCard } from "./MessageDataView";

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const bounce = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
`;

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

const MessageItem = memo(({ msg, isAI, isLast }) => {
  const intent = msg.intent;
  const parsedData = msg.parsedData;

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
          alignItems: "flex-end",
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
              mb: 0.5,
            }}
          >
            <SmartToyIcon sx={{ fontSize: 16, color: "primary.main" }} />
          </Avatar>
        )}

        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            borderRadius: isAI ? "16px 16px 16px 4px" : "16px 16px 4px 16px",
            bgcolor: isAI ? "background.paper" : "primary.main",
            color: isAI ? "text.primary" : "white",
            border: "1px solid",
            borderColor: isAI ? "grey.200" : "transparent",
            boxShadow: isAI ? "0 2px 4px rgba(0,0,0,0.02)" : "none",
          }}
        >
          {isAI && isLast ? (
            <Typewriter text={msg.text} speed={15} />
          ) : (
            <Typography
              variant="body2"
              sx={{
                fontWeight: 500,
                lineHeight: 1.5,
                fontSize: { xs: "0.9rem", sm: "0.875rem" },
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {msg.text}
            </Typography>
          )}

          {isAI && (
            <Box sx={{ color: "text.primary" }}>
              {intent === "query_spending" && parsedData && (
                <SpendingSummary data={parsedData} />
              )}
              {intent === "get_insights" && parsedData && (
                <InsightCard data={parsedData} />
              )}
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  );
});

// const MessageItem = memo(({ msg, isAI, isLast }) => {
//   const theme = useTheme();

//   return (
//     <Box
//       sx={{
//         display: "flex",
//         flexDirection: "column",
//         alignItems: isAI ? "flex-start" : "flex-end",
//         animation: `${fadeIn} 0.3s ease-out`,
//       }}
//     >
//       <Box
//         sx={{
//           display: "flex",
//           alignItems: "flex-end",
//           gap: 1,
//           maxWidth: "85%",
//         }}
//       >
//         {isAI && (
//           <Avatar
//             sx={{
//               width: 28,
//               height: 28,
//               bgcolor: "background.paper",
//               border: "1px solid",
//               borderColor: "divider",
//             }}
//           >
//             <SmartToyIcon sx={{ fontSize: 16, color: "primary.main" }} />
//           </Avatar>
//         )}

//         <Paper
//           elevation={0}
//           sx={{
//             p: 1.5,
//             borderRadius: isAI ? "16px 16px 16px 4px" : "16px 16px 4px 16px",
//             bgcolor: isAI ? "background.paper" : "primary.main",
//             color: isAI ? "text.primary" : "white",
//             border: "1px solid",
//             borderColor: isAI ? "grey.200" : "transparent",
//             background: !isAI ? theme.palette.primary.main : undefined,
//           }}
//         >
//           {isAI && isLast ? (
//             <Typewriter text={msg.text} speed={15} />
//           ) : (
//             <Typography
//               variant="body2"
//               sx={{
//                 fontWeight: 500,
//                 lineHeight: 1.5,
//                 fontSize: { xs: "0.9rem", sm: "0.875rem" },
//                 whiteSpace: "pre-wrap",
//                 wordBreak: "break-word",
//                 overflowWrap: "anywhere",
//               }}
//             >
//               {msg.text}
//             </Typography>
//           )}
//         </Paper>
//       </Box>
//     </Box>
//   );
// });

export const MessageList = ({
  messages,
  isTyping,
  showEmptyState,
  messagesEndRef,
  onSuggestionClick,
  user,
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

  if (showEmptyState) {
    return (
      <MessageEmptyState onSuggestionClick={onSuggestionClick} user={user} />
    );
  }

  return (
    <Stack spacing={2.5} sx={{ p: 2, pb: 8 }}>
      {messages.map((msg, index) => (
        <MessageItem
          key={msg.id || index}
          msg={msg}
          isAI={msg.sender === "ai"}
          isLast={index === messages.length - 1}
        />
      ))}

      {isTyping && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </Stack>
  );
};

export default MessageList;
