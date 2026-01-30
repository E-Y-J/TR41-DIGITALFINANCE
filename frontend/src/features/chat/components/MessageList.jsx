import {
  Box,
  Stack,
  Typography,
  Avatar,
  Paper,
  keyframes,
  Card,
  CardActionArea,
  Grid,
} from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import Typewriter from "./Typewriter";

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
`;

const fadeInSlide = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const SUGGESTIONS = [
  {
    text: "Analyze my spending trends",
    icon: <TrendingUpIcon sx={{ color: "#6366f1" }} />,
  },
  {
    text: "What are my upcoming bills?",
    icon: <ReceiptLongIcon sx={{ color: "#f59e0b" }} />,
  },
  {
    text: "Create a budget for travel",
    icon: <FlightTakeoffIcon sx={{ color: "#10b981" }} />,
  },
];

const TypingIndicator = () => (
  <Box sx={{ display: "flex", gap: 0.6, ml: 5.5, mb: 2, alignItems: "center" }}>
    {[0, 1, 2].map((i) => (
      <Box
        key={i}
        sx={{
          width: 8,
          height: 8,
          bgcolor: "primary.light",
          borderRadius: "50%",
          animation: `${bounce} 1s infinite ease-in-out both`,
          animationDelay: `${i * 0.16}s`,
        }}
      />
    ))}
  </Box>
);

const EmptyState = ({ onSuggestionClick, user }) => (
  <Box
    sx={{
      height: "100%",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      p: 3,
      textAlign: "center",
    }}
  >
    <Avatar
      sx={{
        width: 64,
        height: 64,
        background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
        mb: 3,
        boxShadow: "0 8px 16px rgba(99, 102, 241, 0.2)",
      }}
    >
      <AutoAwesomeIcon sx={{ fontSize: 32, color: "white" }} />
    </Avatar>

    <Typography variant="h5" fontWeight={800} sx={{ letterSpacing: -0.5 }}>
      Hello, {user}
    </Typography>
    <Typography variant="body1" color="text.secondary" sx={{ mb: 6, mt: 1 }}>
      How can I help you today?
    </Typography>

    <Grid container spacing={2} justifyContent="center" maxWidth={850}>
      {SUGGESTIONS.map((item, index) => (
        <Grid item xs={12} sm={4} key={index}>
          <Card
            elevation={0}
            sx={{
              height: "100%",
              border: "1px solid",
              borderColor: "divider",
              borderRadius: 4,
              transition: "all 0.2s ease-in-out",
              "&:hover": {
                borderColor: "primary.main",
                transform: "translateY(-4px)",
                boxShadow: "0 12px 24px rgba(0,0,0,0.04)",
              },
            }}
          >
            <CardActionArea
              onClick={() => onSuggestionClick(item.text)}
              sx={{
                p: 3,
                height: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
              }}
            >
              <Box sx={{ mb: 2, display: "flex" }}>{item.icon}</Box>
              <Typography
                variant="body2"
                fontWeight={700}
                color="text.primary"
                textAlign="left"
              >
                {item.text}
              </Typography>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
);

export const MessageList = ({
  messages,
  isTyping,
  messagesEndRef,
  onSuggestionClick,
  user,
}) => {
  if (messages.length === 0) {
    return <EmptyState onSuggestionClick={onSuggestionClick} user={user} />;
  }

  return (
    <Stack spacing={3} sx={{ p: 2, overflowY: "auto" }}>
      {messages.map((msg) => {
        const isAI = msg.sender === "ai";

        return (
          <Box
            key={msg.id}
            sx={{
              display: "flex",
              justifyContent: isAI ? "flex-start" : "flex-end",
              alignItems: "flex-start",
              animation: `${fadeInSlide} 0.4s ease-out forwards`,
              position: "relative",
            }}
          >
            {isAI && (
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  mr: 2,
                  mt: 0.5,
                  bgcolor: "transparent",
                  border: "1px solid",
                  borderColor: "divider",
                  color: "primary.main",
                }}
              >
                <SmartToyIcon sx={{ fontSize: 20 }} />
              </Avatar>
            )}

            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                px: 2,
                maxWidth: "80%",
                bgcolor: isAI ? "transparent" : "primary.main",
                color: isAI ? "text.primary" : "white",
                border: "1px solid",
                borderColor: isAI ? "divider" : "primary.main",
                borderRadius: 3,
                position: "relative",

                ...(isAI && {
                  "&::before": {
                    content: '""',
                    position: "absolute",
                    left: "-6px",
                    top: "16px",
                    width: "10px",
                    height: "10px",
                    bgcolor: "background.paper",
                    borderLeft: "1px solid",
                    borderBottom: "1px solid",
                    borderColor: "divider",
                    transform: "rotate(45deg)",
                  },
                }),

                ...(!isAI && {
                  borderBottomRightRadius: 1,
                }),
              }}
            >
              {isAI ? (
                <Typewriter text={msg.text} />
              ) : (
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 500, lineHeight: 1.5 }}
                >
                  {msg.text}
                </Typography>
              )}
            </Paper>
          </Box>
        );
      })}

      {isTyping && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </Stack>
  );
};

export default MessageList;
