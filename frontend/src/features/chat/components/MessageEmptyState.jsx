import {
  Box,
  Typography,
  Grid,
  Card,
  CardActionArea,
  useTheme,
  useMediaQuery,
  Grow,
  alpha,
} from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import BarChartIcon from "@mui/icons-material/BarChart";
import PieChartIcon from "@mui/icons-material/PieChart";

const SUGGESTIONS = [
  {
    text: "Summary of recent transactions",
    fullText: "Show me a summary of my recent transactions.",
    icon: <ChatBubbleOutlineIcon />,
  },
  {
    text: "Monthly budget status",
    fullText: "How am I doing on my budget for this month?",
    icon: <PieChartIcon />,
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
  const isDarkMode = theme.palette.mode === "dark";

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        p: { xs: 2, sm: 4 },
        maxWidth: 850,
        margin: "0 auto",
      }}
    >
      <Box sx={{ textAlign: "center", mb: 6 }}>
        <Typography
          variant={isMobile ? "h5" : "h4"}
          fontWeight={800}
          gutterBottom
          sx={{
            // Improved gradient for dark mode compatibility
            background: isDarkMode
              ? `linear-gradient(45deg, ${theme.palette.primary.light}, ${theme.palette.common.white})`
              : `linear-gradient(45deg, ${theme.palette.text.primary}, ${theme.palette.grey[600]})`,
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
          How can I assist you?
        </Typography>
      </Box>

      <Grid
        container
        spacing={2}
        justifyContent="center"
        sx={{ width: "100%" }}
      >
        {SUGGESTIONS.map((item, index) => (
          <Grid item xs={12} sm={4} key={index}>
            <Grow in timeout={400 + index * 150}>
              {/* FIX: Wrap Card in a div to provide a clean DOM node for the transition */}
              <div>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 4,
                    border: "1px solid",
                    borderColor: "divider",
                    bgcolor: "background.paper",
                    transition: "all 0.2s ease-in-out",
                    "&:hover": {
                      borderColor: "primary.main",
                      bgcolor: alpha(
                        theme.palette.primary.main,
                        isDarkMode ? 0.08 : 0.04,
                      ),
                      transform: "translateY(-4px)",
                      boxShadow: isDarkMode
                        ? `0 8px 24px ${alpha(theme.palette.common.black, 0.6)}`
                        : "0 8px 24px rgba(0,0,0,0.06)",
                    },
                  }}
                >
                  <CardActionArea
                    onClick={() => onSuggestionClick(item.fullText)}
                    sx={{
                      p: 2,
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-start",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 44,
                        height: 44,
                        borderRadius: "12px",
                        // Dynamic background for the icon container
                        bgcolor: isDarkMode
                          ? alpha(theme.palette.primary.main, 0.2)
                          : alpha(theme.palette.primary.main, 0.1),
                        color: "primary.main",
                        mb: 2,
                        "& svg": { fontSize: 22 },
                      }}
                    >
                      {item.icon}
                    </Box>

                    <Typography
                      variant="body2"
                      fontWeight={700}
                      sx={{
                        lineHeight: 1.4,
                        textAlign: "left",
                        color: "text.primary",
                      }}
                    >
                      {item.text}
                    </Typography>
                  </CardActionArea>
                </Card>
              </div>
            </Grow>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default MessageEmptyState;
