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
  useTheme,
  Stack,
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
  });
};

export default function NotificationsPage() {
  const theme = useTheme();
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

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 900, mx: "auto" }}>
      <Paper
        variant="outlined"
        sx={{
          borderRadius: 4,
          bgcolor: (theme) =>
            theme.palette.mode === "dark"
              ? alpha(theme.palette.background.paper, 0.4)
              : "background.paper",
          overflow: "hidden",
          backgroundImage: "none",
        }}
      >
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{
            p: 3,
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <NotificationsIcon color="primary" />
            <Box>
              <Typography variant="h6" fontWeight={900}>
                Notifications
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={600}
              >
                {unreadCount > 0 ? `${unreadCount} UNREAD` : "ALL CAUGHT UP"}
              </Typography>
            </Box>
          </Stack>

          {unreadCount > 0 && (
            <Button
              variant="text"
              size="small"
              startIcon={<DoneAllIcon />}
              onClick={() => markAllAsReadMutation.mutate()}
              sx={{ fontWeight: 800, textTransform: "none" }}
            >
              Mark all read
            </Button>
          )}
        </Stack>

        <Box sx={{ minHeight: 300 }}>
          {isLoading ? (
            <Stack alignItems="center" justifyContent="center" sx={{ py: 10 }}>
              <CircularProgress size={32} />
            </Stack>
          ) : notifications.length === 0 ? (
            <Stack
              alignItems="center"
              justifyContent="center"
              sx={{ py: 10, opacity: 0.5 }}
            >
              <NotificationsIcon sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="body2">No notifications found</Typography>
            </Stack>
          ) : (
            <List disablePadding>
              {notifications.map((notification, index) => {
                const typeKey = notification.type?.toLowerCase();
                const typeConfig =
                  NOTIFICATION_TYPE_CONFIG[typeKey] ||
                  NOTIFICATION_TYPE_CONFIG.default;
                const isUnread = notification.status === "unread";

                const chipColor =
                  theme.palette[typeConfig.color]?.main ||
                  theme.palette.text.secondary;

                return (
                  <Box key={notification.id}>
                    <ListItem
                      disablePadding
                      secondaryAction={
                        isUnread && (
                          <Tooltip title="Mark as read" arrow placement="left">
                            <IconButton
                              size="small"
                              onClick={() =>
                                markAsReadMutation.mutate(notification.id)
                              }
                              sx={{ color: "primary.main" }}
                            >
                              <CircleIcon sx={{ fontSize: 10 }} />
                            </IconButton>
                          </Tooltip>
                        )
                      }
                    >
                      <ListItemButton
                        onClick={() =>
                          isUnread && markAsReadMutation.mutate(notification.id)
                        }
                        sx={{
                          py: 2,
                          px: 3,
                          transition: "0.2s",
                          bgcolor: isUnread
                            ? alpha("#3b82f6", 0.04)
                            : "transparent",
                          "&:hover": { bgcolor: alpha("#3b82f6", 0.08) },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Stack
                              direction="row"
                              spacing={1.5}
                              alignItems="center"
                              sx={{ mb: 0.5 }}
                            >
                              <Typography
                                variant="subtitle2"
                                fontWeight={isUnread ? 900 : 600}
                              >
                                {notification.message}
                              </Typography>
                              <Chip
                                label={typeConfig.label}
                                size="small"
                                sx={{
                                  height: 20,
                                  fontSize: "0.625rem",
                                  fontWeight: 900,
                                  textTransform: "uppercase",
                                  letterSpacing: "0.05em",

                                  bgcolor: alpha(chipColor, 0.12),
                                  color: isUnread
                                    ? chipColor
                                    : alpha(chipColor, 0.7),
                                  border: `1px solid ${alpha(chipColor, 0.2)}`,
                                  borderRadius: "6px",
                                  "& .MuiChip-label": { px: 1 },
                                }}
                              />
                            </Stack>
                          }
                          secondary={
                            <Typography
                              variant="caption"
                              color="text.disabled"
                              fontWeight={600}
                            >
                              {formatDate(notification.created_at)}
                            </Typography>
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

        {totalPages > 1 && (
          <Stack
            alignItems="center"
            sx={{ p: 2, borderTop: "1px solid", borderColor: "divider" }}
          >
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, val) => setPage(val)}
              size="small"
              color="primary"
            />
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
