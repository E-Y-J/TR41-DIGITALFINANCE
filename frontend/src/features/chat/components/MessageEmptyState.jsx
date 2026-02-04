import {
  Box,
  Typography,
  Grid,
  Card,
  CardActionArea,
  useTheme,
  useMediaQuery,
  Grow,
} from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import BarChartIcon from "@mui/icons-material/BarChart";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";

const SUGGESTIONS = [
  {
    text: "Summary of recent transactions",
    fullText: "Show me a summary of my recent transactions.",
    icon: <ChatBubbleOutlineIcon />,
  },
  {
    text: "Current account balance",
    fullText: "What is my current account balance?",
    icon: <AccountBalanceWalletIcon />,
  },
  {
    text: "Insights on spending habits",
    fullText: "Provide insights on my spending habits.",
    icon: <BarChartIcon />,
  },
];

const MessageEmptyState = ({ onSuggestionClick, user }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        p: { xs: 2, sm: 4 },
        maxWidth: 450,
        margin: "0 auto",
      }}
    >
      <Box sx={{ textAlign: "center", mb: 4 }}>
        <Typography
          variant={isMobile ? "h5" : "h4"}
          fontWeight={800}
          gutterBottom
          sx={{
            background: `linear-gradient(45deg, ${theme.palette.text.primary}, ${theme.palette.grey[600]})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: -0.5,
          }}
        >
          Hey, {user || "there"}!
        </Typography>

        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ px: 2, lineHeight: 1.5 }}
        >
          How can I help you make sense of your money today?
        </Typography>
      </Box>

      <Grid container spacing={1.5} sx={{ width: "100%" }}>
        {SUGGESTIONS.map((item, index) => (
          <Grid item xs={12} key={index}>
            <Grow in timeout={400 + index * 150}>
              <Card
                elevation={0}
                sx={{
                  borderRadius: 4,
                  border: "1px solid",
                  borderColor: "divider",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    borderColor: "primary.main",
                    bgcolor: "rgba(25, 118, 210, 0.02)",
                    transform: "translateY(-2px)",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                  },
                }}
              >
                <CardActionArea
                  onClick={() => onSuggestionClick(item.fullText)}
                  sx={{
                    p: 2,
                    display: "flex",
                    justifyContent: "flex-start",
                    alignItems: "center",
                    gap: 2,
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      width: 44,
                      height: 44,
                      borderRadius: "12px",
                      bgcolor: "primary.lighter",
                      color: "primary.main",
                      "& svg": { fontSize: 22 },
                    }}
                  >
                    {item.icon}
                  </Box>

                  <Box sx={{ textAlign: "left" }}>
                    <Typography
                      variant="body2"
                      fontWeight={600}
                      sx={{ lineHeight: 1.2, mb: 0.2 }}
                    >
                      {item.text}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Tap to ask
                    </Typography>
                  </Box>
                </CardActionArea>
              </Card>
            </Grow>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default MessageEmptyState;
