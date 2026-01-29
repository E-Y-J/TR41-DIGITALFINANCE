import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Button,
} from "@mui/material";
import EditNoteIcon from "@mui/icons-material/EditNote";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";

const ChatSidebar = ({
  conversations,
  activeChatId,
  onSelectChat,
  onNewChat,
  isMobile = false,
}) => {
  return (
    <Box
      sx={{
        width: isMobile ? "100%" : 280,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        borderLeft: isMobile ? "none" : "1px solid",
        borderColor: "divider",
        bgcolor: "transparent",
        pb: isMobile ? 4 : 0,
      }}
    >
      <Box
        sx={{
          p: 2,
          display: "flex",
          justifyContent: isMobile ? "flex-start" : "center",
        }}
      >
        <Button
          variant="contained"
          startIcon={<EditNoteIcon />}
          onClick={onNewChat}
          sx={{
            py: 0.8,
            px: 3,
            borderRadius: 10,
            textTransform: "none",
            fontWeight: 700,
            fontSize: "0.85rem",
            boxShadow: "0 4px 12px rgba(33, 150, 243, 0.2)",
            background: "linear-gradient(135deg, #2196F3 0%, #00BCD4 100%)",
            "&:hover": {
              background: "linear-gradient(135deg, #1976D2 0%, #0097A7 100%)",
            },
          }}
        >
          New Chat
        </Button>
      </Box>

      <Box sx={{ flexGrow: 1, overflowY: "auto", px: 1.5 }}>
        <Box
          sx={{ display: "flex", alignItems: "center", px: 1.5, mb: 1, mt: 1 }}
        >
          <Typography
            variant="caption"
            sx={{
              fontWeight: 800,
              color: "text.secondary",
              letterSpacing: "1px",
            }}
          >
            RECENT
          </Typography>
          <Box
            sx={{
              flexGrow: 1,
              height: "1px",
              bgcolor: "divider",
              ml: 2,
              opacity: 0.5,
            }}
          />
        </Box>

        <List sx={{ p: 0 }}>
          {conversations.map((chat) => {
            const isActive = activeChatId === chat.id;
            return (
              <ListItem key={chat.id} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  selected={isActive}
                  onClick={() => onSelectChat(chat.id)}
                  sx={{
                    borderRadius: 2.5,
                    transition: "all 0.2s",

                    "&.Mui-selected": {
                      bgcolor: "background.paper",
                      boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                      "&::before": {
                        content: '""',
                        position: "absolute",
                        left: 0,
                        height: "60%",
                        width: "4px",
                        borderRadius: "0 4px 4px 0",
                        bgcolor: "primary.main",
                      },
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <ChatBubbleOutlineIcon sx={{ fontSize: 18 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={chat.title}
                    primaryTypographyProps={{
                      fontSize: "0.9rem",
                      fontWeight: isActive ? 700 : 500,
                      noWrap: true,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );
};

export default ChatSidebar;
