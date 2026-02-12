import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  Button,
  CircularProgress,
  Pagination,
  alpha,
} from "@mui/material";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import CircleIcon from "@mui/icons-material/Circle";
import NotificationsIcon from "@mui/icons-material/Notifications";
import {
  useGetNotifications,
  useMarkAsRead,
  useMarkAllAsRead,
  useGetUnreadCount,
} from "../features/notifications";

// Map notification types to user-friendly labels and colors
const NOTIFICATION_TYPE_CONFIG = {
  default: { label: "General", color: "default" },
  new_transaction: { label: "Transaction", color: "primary" },
  deleted_transaction: { label: "Deleted", color: "error" },
  edited_profile: { label: "Profile", color: "info" },
  weekly_summary_ready: { label: "Summary", color: "success" },
  category_updated: { label: "Category", color: "warning" },
  budget_warning: { label: "Budget Alert", color: "warning" },
  budget_exceeded: { label: "Over Budget", color: "error" },
  ai_clarification: { label: "AI Chat", color: "info" },
};

const getTypeConfig = (type) => {
  return NOTIFICATION_TYPE_CONFIG[type] || NOTIFICATION_TYPE_CONFIG.default;
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

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
  });
};

export default function NotificationsPage() {
  const [page, setPage] = useState(1);
  const perPage = 20;

  const { data: notificationsData, isLoading } = useGetNotifications({
    page,
    per_page: perPage,
  });
  const { data: unreadCount = 0 } = useGetUnreadCount();

  const markAsReadMutation = useMarkAsRead();
  const markAllAsReadMutation = useMarkAllAsRead();

  const notifications = notificationsData?.items ?? [];
  const totalPages = Math.ceil((notificationsData?.total ?? 0) / perPage);

  const handleMarkAsRead = (notificationId) => {
    markAsReadMutation.mutate(notificationId);
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: "auto" }}>
      <Paper
        elevation={3}
        sx={{
          borderRadius: 4,
          border: "1px solid",
          borderColor: "grey.200",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 3,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: 1,
            borderColor: "divider",
            bgcolor: (theme) => alpha(theme.palette.primary.main, 0.02),
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <NotificationsIcon color="primary" sx={{ fontSize: 28 }} />
            <Box>
              <Typography variant="h5" fontWeight={700}>
                Notifications
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {unreadCount > 0
                  ? `${unreadCount} unread notification${unreadCount > 1 ? "s" : ""}`
                  : "All caught up!"}
              </Typography>
            </Box>
          </Box>

          {unreadCount > 0 && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<DoneAllIcon />}
              onClick={handleMarkAllAsRead}
              disabled={markAllAsReadMutation.isPending}
              sx={{ borderRadius: 2 }}
            >
              Mark all as read
            </Button>
          )}
        </Box>

        {/* Notifications List */}
        <Box sx={{ minHeight: 400 }}>
          {isLoading ? (
            <Box
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                minHeight: 300,
              }}
            >
              <CircularProgress />
            </Box>
          ) : notifications.length === 0 ? (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                minHeight: 300,
                color: "text.secondary",
              }}
            >
              <NotificationsIcon sx={{ fontSize: 64, mb: 2, opacity: 0.2 }} />
              <Typography variant="h6" fontWeight={500}>
                No notifications yet
              </Typography>
              <Typography variant="body2">
                We'll notify you when something important happens
              </Typography>
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
                          <Tooltip title="Mark as read" placement="left">
                            <IconButton
                              edge="end"
                              size="small"
                              onClick={() => handleMarkAsRead(notification.id)}
                              disabled={markAsReadMutation.isPending}
                              sx={{ mr: 1 }}
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
                        onClick={() => {
                          if (isUnread) handleMarkAsRead(notification.id);
                        }}
                        sx={{
                          py: 2.5,
                          px: 3,
                          pr: isUnread ? 7 : 3,
                          bgcolor: isUnread
                            ? (theme) => alpha(theme.palette.primary.main, 0.04)
                            : "transparent",
                          borderLeft: "4px solid",
                          borderColor: isUnread ? "primary.main" : "transparent",
                          transition: "all 0.2s ease-in-out",
                          "&:hover": {
                            bgcolor: (theme) =>
                              alpha(theme.palette.primary.main, 0.08),
                          },
                        }}
                      >
                        <ListItemText
                          disableTypography
                          primary={
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1.5,
                                mb: 1,
                              }}
                            >
                              <Typography
                                variant="subtitle1"
                                fontWeight={isUnread ? 700 : 500}
                                color={
                                  isUnread ? "text.primary" : "text.secondary"
                                }
                              >
                                {notification.title || "Notification"}
                              </Typography>
                              <Chip
                                label={typeConfig.label}
                                size="small"
                                color={typeConfig.color}
                                variant={isUnread ? "filled" : "outlined"}
                                sx={{ height: 22, fontSize: "0.7rem" }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{ mb: 0.5 }}
                              >
                                {notification.message}
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.disabled"
                              >
                                {formatDate(notification.created_at)}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                    {index < notifications.length - 1 && <Divider />}
                  </Box>
                );
              })}
            </List>
          )}
        </Box>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box
            sx={{
              p: 2,
              display: "flex",
              justifyContent: "center",
              borderTop: 1,
              borderColor: "divider",
            }}
          >
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, newPage) => setPage(newPage)}
              color="primary"
              shape="rounded"
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
}
