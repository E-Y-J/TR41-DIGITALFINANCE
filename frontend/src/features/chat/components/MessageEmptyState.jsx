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

  const displaySuggestions = isMobile ? SUGGESTIONS.slice(0, 1) : SUGGESTIONS;

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
      <Box sx={{ textAlign: "center", mb: { xs: 3, sm: 6 } }}>
        <Typography
          variant={isMobile ? "h5" : "h4"}
          fontWeight={900}
          gutterBottom
          sx={{
            background: isDarkMode
              ? `linear-gradient(45deg, ${theme.palette.primary.light}, ${theme.palette.common.white})`
              : `linear-gradient(45deg, ${theme.palette.text.primary}, ${theme.palette.grey[600]})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: -1,
          }}
        >
          Hey, {user || "there"}!
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ px: 2, lineHeight: 1.4, fontWeight: 500 }}
        >
          How can I assist you today?
        </Typography>
      </Box>

      <Grid
        container
        spacing={2}
        justifyContent="center"
        sx={{ width: "100%", maxWidth: { xs: 300, sm: "100%" } }}
      >
        {displaySuggestions.map((item, index) => (
          <Grid item xs={12} sm={4} key={index}>
            <Grow in timeout={400 + index * 150}>
              <div>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                    bgcolor: "background.paper",
                    backgroundImage: "none",
                    transition: "all 0.2s ease-in-out",
                    "&:hover": {
                      borderColor: "primary.main",
                      transform: "translateY(-4px)",
                    },
                  }}
                >
                  <CardActionArea
                    onClick={() => onSuggestionClick(item.fullText)}
                    sx={{
                      p: 2,
                      display: "flex",

                      flexDirection: { xs: "row", sm: "column" },
                      alignItems: "center",
                      gap: { xs: 2, sm: 0 },
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: { xs: 36, sm: 44 },
                        height: { xs: 36, sm: 44 },
                        borderRadius: "10px",
                        bgcolor: alpha(
                          theme.palette.primary.main,
                          isDarkMode ? 0.2 : 0.1,
                        ),
                        color: "primary.main",
                        mb: { xs: 0, sm: 2 },
                        flexShrink: 0,
                        "& svg": { fontSize: { xs: 18, sm: 22 } },
                      }}
                    >
                      {item.icon}
                    </Box>

                    <Typography
                      variant="caption"
                      fontWeight={700}
                      sx={{
                        lineHeight: 1.3,
                        textAlign: { xs: "left", sm: "center" },
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
