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
  isMobile,
}) => (
  <Box
    sx={{
      width: isMobile ? "100%" : 280,
      height: "100%",
      display: "flex",
      flexDirection: "column",
      borderLeft: isMobile ? "none" : "1px solid divider",
    }}
  >
    <Box sx={{ p: 2 }}>
      <Button
        fullWidth
        variant="contained"
        startIcon={<EditNoteIcon />}
        onClick={onNewChat}
        sx={{
          borderRadius: 3,
          textTransform: "none",
          py: 1,
          fontWeight: 700,
          background: "linear-gradient(135deg, #2196F3, #00BCD4)",
        }}
      >
        New Chat
      </Button>
    </Box>

    <Box sx={{ flex: 1, overflowY: "auto", px: 1.5 }}>
      <Typography
        variant="caption"
        sx={{
          fontWeight: 700,
          color: "text.secondary",
          ml: 1,
          mb: 1,
          display: "block",
        }}
      >
        RECENT ACTIVITY
      </Typography>

      <List>
        {conversations.map((chat) => (
          <ListItem key={chat.id} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={activeChatId === chat.id}
              onClick={() => onSelectChat(chat.id)}
              sx={{
                borderRadius: 2,
                "&.Mui-selected": {
                  bgcolor: "white",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <ChatBubbleOutlineIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={chat.title}
                slotProps={{
                  primary: {
                    fontSize: "0.85rem",
                    noWrap: true,
                    fontWeight: activeChatId === chat.id ? 700 : 500,
                    sx: {
                      color:
                        activeChatId === chat.id
                          ? "text.primary"
                          : "text.secondary",
                    },
                  },
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  </Box>
);

export default ChatSidebar;
