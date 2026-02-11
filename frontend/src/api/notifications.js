/**
 * Notifications API functions
 * Endpoints for fetching and managing user notifications
 */

export const getNotifications = async (apiClient, params = {}) => {
  const data = await apiClient.get("/notifications", {
    params: params,
  });
  return data;
};

export const getUnreadCount = async (apiClient) => {
  const data = await apiClient.get("/notifications/unread-count");
  return data;
};

export const markAsRead = async (apiClient, notificationId) => {
  const data = await apiClient.patch(`/notifications/${notificationId}/read`);
  return data;
};

export const markAllAsRead = async (apiClient) => {
  const data = await apiClient.patch("/notifications/read-all");
  return data;
};

export const deleteNotification = async (apiClient, notificationId) => {
  const data = await apiClient.delete(`/notifications/${notificationId}`);
  return data;
};
