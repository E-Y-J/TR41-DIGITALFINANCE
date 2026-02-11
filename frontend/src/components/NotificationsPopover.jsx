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
  alpha,
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

// Moved outside to prevent re-creation on every render
const getTypeConfig = (type) => {
  return NOTIFICATION_TYPE_CONFIG[type] || NOTIFICATION_TYPE_CONFIG.default;
};

// Moved outside to prevent re-creation on every render
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

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
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

  const handleOpen = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleMarkAsRead = (notificationId, event) => {
    event.stopPropagation();
    markAsReadMutation.mutate(notificationId);
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton
          size="large"
          color="inherit"
          onClick={handleOpen}
          sx={{ mr: 1 }}
          aria-haspopup="true"
          aria-expanded={open ? "true" : undefined}
        >
          <Badge
            badgeContent={unreadCount}
            color="error"
            max={99}
            overlap="circular"
            sx={{
              "& .MuiBadge-badge": {
                fontWeight: "bold",
                boxShadow: (theme) =>
                  `0 0 0 2px ${theme.palette.background.paper}`,
              },
            }}
          >
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
        slotProps={{
          paper: {
            sx: {
              width: 360,
              // Responsive height fix + modern border radius
              maxHeight: "min(480px, calc(100vh - 32px))",
              borderRadius: 3,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              boxShadow: (theme) => theme.shadows[8],
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
            bgcolor: (theme) => alpha(theme.palette.background.default, 0.9),
            backdropFilter: "blur(8px)",
          }}
        >
          <Typography variant="h6" fontWeight="800" fontSize="1.1rem">
            Notifications
          </Typography>
          {unreadCount > 0 && (
            <Tooltip title="Mark all as read" placement="left">
              <IconButton
                size="small"
                onClick={handleMarkAllAsRead}
                disabled={markAllAsReadMutation.isPending}
                color="primary"
                sx={{
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                }}
              >
                <DoneAllIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Notifications List */}
        <Box sx={{ flex: 1, overflowY: "auto", overflowX: "hidden" }}>
          {isLoading ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                minHeight: 250, // Prevents layout snapping
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
                justifyContent: "center",
                minHeight: 250, // Prevents layout snapping
                color: "text.secondary",
              }}
            >
              <NotificationsIcon sx={{ fontSize: 48, mb: 1, opacity: 0.2 }} />
              <Typography variant="body2" fontWeight="500">
                You're all caught up!
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {notifications.map((notification, index) => {
                const typeConfig = getTypeConfig(
                  notification.notification_type,
                );
                const isUnread = notification.status === "unread";

                return (
                  <Box key={notification.id}>
                    <ListItem
                      disablePadding
                      secondaryAction={
                        isUnread && (
                          <Tooltip title="Mark as read" placement="left">
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
                                sx={{ fontSize: 12, color: "primary.main" }}
                              />
                            </IconButton>
                          </Tooltip>
                        )
                      }
                    >
                      <ListItemButton
                        onClick={(e) => {
                          if (isUnread) handleMarkAsRead(notification.id, e);
                        }}
                        sx={{
                          py: 2,
                          px: 2,
                          // CRITICAL: Prevent text from going under the circle icon
                          pr: isUnread ? 6 : 2,
                          // Visual unread indicator
                          bgcolor: isUnread ? "action.hover" : "transparent",
                          borderLeft: "4px solid",
                          borderColor: isUnread
                            ? "primary.main"
                            : "transparent",
                          transition: "all 0.2s ease-in-out",
                        }}
                      >
                        <ListItemText
                          disableTypography
                          primary={
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                                mb: 0.75,
                              }}
                            >
                              <Typography
                                variant="subtitle2"
                                fontWeight={isUnread ? 700 : 500}
                                color={
                                  isUnread ? "text.primary" : "text.secondary"
                                }
                                sx={{ flex: 1, lineHeight: 1.2 }}
                              >
                                {notification.title}
                              </Typography>
                              <Chip
                                label={typeConfig.label}
                                size="small"
                                color={typeConfig.color}
                                variant={isUnread ? "filled" : "outlined"}
                                sx={{
                                  height: 20,
                                  fontSize: "0.65rem",
                                  fontWeight: 600,
                                }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box
                              sx={{ display: "flex", flexDirection: "column" }}
                            >
                              <Typography
                                variant="body2"
                                color={
                                  isUnread ? "text.secondary" : "text.disabled"
                                }
                                sx={{
                                  display: "-webkit-box",
                                  WebkitLineClamp: 2,
                                  WebkitBoxOrient: "vertical",
                                  overflow: "hidden",
                                  lineHeight: 1.4,
                                }}
                              >
                                {notification.message}
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.disabled"
                                fontWeight="500"
                                sx={{ mt: 1, display: "block" }}
                              >
                                {formatDate(notification.created_at)}
                              </Typography>
                            </Box>
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
              p: 1.5,
              borderTop: 1,
              borderColor: "divider",
              textAlign: "center",
              bgcolor: "background.paper",
            }}
          >
            <Button
              size="small"
              color="primary"
              sx={{ fontWeight: 600, textTransform: "none", borderRadius: 2 }}
            >
              View All Notifications
            </Button>
          </Box>
        )}
      </Popover>
    </>
  );
};

export default NotificationsPopover;
