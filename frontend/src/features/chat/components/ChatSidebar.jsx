import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Button,
  IconButton,
  Tooltip,
} from "@mui/material";
import EditNoteIcon from "@mui/icons-material/EditNote";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";

const ChatSidebar = ({
  conversations,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  isMobile,
}) => (
  <Box
    sx={{
      width: isMobile ? "100%" : 280,
      height: "100%",
      display: "flex",
      flexDirection: "column",
      borderLeft: isMobile ? "none" : "1px solid",
      bgcolor: "background.default",
      borderColor: "divider",
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
          py: 1.2,
          fontWeight: 700,
          background: "linear-gradient(135deg, #2196F3, #00BCD4)",
          boxShadow: "0 4px 12px rgba(33, 150, 243, 0.25)",
        }}
      >
        New Chat
      </Button>
    </Box>

    <Box sx={{ flex: 1, overflowY: "auto", px: 1.5 }}>
      <Typography
        variant="caption"
        sx={{
          fontWeight: 800,
          color: "text.secondary",
          ml: 1.5,
          mb: 1.5,
          display: "block",
          letterSpacing: "0.5px",
        }}
      >
        RECENT ACTIVITY
      </Typography>

      <List sx={{ p: 0 }}>
        {conversations.map((chat) => {
          const isActive = activeChatId === chat.id;

          return (
            <ListItem key={chat.id} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                selected={isActive}
                onClick={() => onSelectChat(chat.id)}
                sx={{
                  borderRadius: "12px",
                  transition: "all 0.2s ease",
                  position: "relative",
                  overflow: "hidden",

                  // Default Hover
                  "&:hover": {
                    bgcolor: "action.hover",
                  },

                  // ACTIVE STATE
                  "&.Mui-selected": {
                    bgcolor: "background.paper",
                    boxShadow: (theme) =>
                      theme.palette.mode === "dark"
                        ? "0 4px 20px rgba(0,0,0,0.5)"
                        : "0 4px 12px rgba(0,0,0,0.06)",
                    "&:hover": { bgcolor: "background.paper" },

                    // The "Selection Bar" Indicator
                    "&::before": {
                      content: '""',
                      position: "absolute",
                      left: 0,
                      top: "20%",
                      bottom: "20%",
                      width: "4px",
                      borderRadius: "0 4px 4px 0",
                      bgcolor: "primary.main",
                      boxShadow: "2px 0 8px rgba(33, 150, 243, 0.4)",
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <ChatBubbleOutlineIcon
                    fontSize="small"
                    color={isActive ? "primary" : "inherit"}
                    sx={{ transition: "color 0.2s" }}
                  />
                </ListItemIcon>

                <ListItemText
                  primary={chat.title}
                  slotProps={{
                    primary: {
                      fontSize: "0.85rem",
                      noWrap: true,
                      fontWeight: isActive ? 700 : 500,
                      sx: {
                        color: isActive ? "text.primary" : "text.secondary",
                      },
                    },
                  }}
                />

                {isActive && onDeleteChat && (
                  <Tooltip title="Delete chat" placement="left">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteChat(chat.id);
                      }}
                      sx={{
                        opacity: 0.6,
                        "&:hover": {
                          opacity: 1,
                          color: "error.main",
                        },
                      }}
                    >
                      <DeleteOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  </Box>
);

export default ChatSidebar;
