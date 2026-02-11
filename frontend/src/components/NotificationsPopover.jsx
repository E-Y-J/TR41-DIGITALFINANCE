import { useState } from "react";
import {
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  IconButton,
  Badge,
  Tooltip,
  Divider,
  Button,
  CircularProgress,
  Chip,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import CircleIcon from "@mui/icons-material/Circle";
import {
  useGetNotifications,
  useGetUnreadCount,
  useMarkAsRead,
  useMarkAllAsRead,
} from "../features/notifications";

// Map notification types to user-friendly labels and colors
const NOTIFICATION_TYPE_CONFIG = {
  default: { label: "General", color: "default" },
  new_transaction: { label: "Transaction", color: "primary" },
  deleted_transaction: { label: "Deleted", color: "error" },
  edited_profile: { label: "Profile", color: "info" },
  weekly_summary_ready: { label: "Summary", color: "success" },
  category_updated: { label: "Category", color: "warning" },
};

const NotificationsPopover = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Fetch notifications and unread count
  const { data: notificationsData, isLoading } = useGetNotifications({
    per_page: 10,
  });
  const { data: unreadCount = 0 } = useGetUnreadCount();

  // Mutations
  const markAsReadMutation = useMarkAsRead();
  const markAllAsReadMutation = useMarkAllAsRead();

  const notifications = notificationsData?.items ?? [];

  const handleOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAsRead = (notificationId, event) => {
    event.stopPropagation();
    markAsReadMutation.mutate(notificationId);
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getTypeConfig = (type) => {
    return NOTIFICATION_TYPE_CONFIG[type] || NOTIFICATION_TYPE_CONFIG.default;
  };

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton
          size="large"
          color="inherit"
          onClick={handleOpen}
          sx={{ mr: 1 }}
        >
          <Badge
            badgeContent={unreadCount}
            color="error"
            max={99}
            overlap="circular"
          >
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        slotProps={{
          paper: {
            sx: {
              width: 360,
              maxHeight: 480,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
            },
          },
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: 1,
            borderColor: "divider",
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            Notifications
          </Typography>
          {unreadCount > 0 && (
            <Tooltip title="Mark all as read">
              <IconButton
                size="small"
                onClick={handleMarkAllAsRead}
                disabled={markAllAsReadMutation.isPending}
              >
                <DoneAllIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Notifications List */}
        <Box sx={{ flex: 1, overflow: "auto" }}>
          {isLoading ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                py: 4,
              }}
            >
              <CircularProgress size={32} />
            </Box>
          ) : notifications.length === 0 ? (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                py: 4,
                color: "text.secondary",
              }}
            >
              <NotificationsIcon sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />
              <Typography variant="body2">No notifications yet</Typography>
            </Box>
          ) : (
            <List disablePadding>
              {notifications.map((notification, index) => {
                const typeConfig = getTypeConfig(notification.notification_type);
                const isUnread = notification.status === "unread";

                return (
                  <Box key={notification.id}>
                    <ListItem
                      disablePadding
                      secondaryAction={
                        isUnread && (
                          <Tooltip title="Mark as read">
                            <IconButton
                              edge="end"
                              size="small"
                              onClick={(e) =>
                                handleMarkAsRead(notification.id, e)
                              }
                              disabled={markAsReadMutation.isPending}
                              sx={{ mr: 0.5 }}
                            >
                              <CircleIcon
                                sx={{ fontSize: 10, color: "primary.main" }}
                              />
                            </IconButton>
                          </Tooltip>
                        )
                      }
                    >
                      <ListItemButton
                        sx={{
                          py: 1.5,
                          px: 2,
                          bgcolor: isUnread
                            ? "action.hover"
                            : "background.paper",
                        }}
                        onClick={(e) => {
                          if (isUnread) {
                            handleMarkAsRead(notification.id, e);
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                                mb: 0.5,
                              }}
                            >
                              <Typography
                                variant="subtitle2"
                                fontWeight={isUnread ? "bold" : "medium"}
                                sx={{ flex: 1 }}
                              >
                                {notification.title}
                              </Typography>
                              <Chip
                                label={typeConfig.label}
                                size="small"
                                color={typeConfig.color}
                                sx={{ height: 20, fontSize: "0.7rem" }}
                              />
                            </Box>
                          }
                          secondary={
                            <>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{
                                  display: "-webkit-box",
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: "vertical",
                                  overflow: "hidden",
                                }}
                              >
                                {notification.message}
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.disabled"
                                sx={{ mt: 0.5, display: "block" }}
                              >
                                {formatDate(notification.created_at)}
                              </Typography>
                            </>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                    {index < notifications.length - 1 && (
                      <Divider component="li" />
                    )}
                  </Box>
                );
              })}
            </List>
          )}
        </Box>

        {/* Footer */}
        {notifications.length > 0 && (
          <Box
            sx={{
              p: 1,
              borderTop: 1,
              borderColor: "divider",
              textAlign: "center",
            }}
          >
            <Button size="small" color="primary">
              View All Notifications
            </Button>
          </Box>
        )}
      </Popover>
    </>
  );
};

export default NotificationsPopover;
