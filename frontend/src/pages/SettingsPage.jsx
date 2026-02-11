import { useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Switch,
  Divider,
  Button,
  Snackbar,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import SecurityIcon from "@mui/icons-material/Security";
import { useGetUser } from "../features/auth/useGetUser";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateUser } from "../api/user";
import { useAxios } from "../hooks/useAxios";
import { useAuth0 } from "@auth0/auth0-react";

export default function SettingsPage() {
  const { data: user, isLoading } = useGetUser();
  const { logout } = useAuth0();
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  // Get current settings from user data with defaults
  const currentSettings = {
    currency: user?.settings?.currency || "USD",
    timezone: user?.settings?.timezone || "UTC",
    theme: user?.settings?.theme || "system",
    notifications: {
      email: user?.settings?.notifications?.email ?? true,
      budget_alerts: user?.settings?.notifications?.budget_alerts ?? true,
      ai_insights: user?.settings?.notifications?.ai_insights ?? true,
    },
  };

  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

  const updateMutation = useMutation({
    mutationFn: (data) => updateUser(apiClient, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      setSnackbar({ open: true, message: "Settings saved!", severity: "success" });
    },
    onError: (error) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.error?.message || "Failed to save settings",
        severity: "error",
      });
    },
  });

  const handleToggle = (key) => {
    const newNotifications = { ...currentSettings.notifications, [key]: !currentSettings.notifications[key] };
    const newSettings = { ...currentSettings, notifications: newNotifications };
    updateMutation.mutate({ settings: newSettings });
  };

  const handleSelectChange = (key, value) => {
    const newSettings = { ...currentSettings, [key]: value };
    updateMutation.mutate({ settings: newSettings });
  };

  const handleLogout = () => {
    logout({ logoutParams: { returnTo: window.location.origin } });
  };

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, maxWidth: 800, mx: "auto" }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        Account Settings
      </Typography>

      {/* Notifications Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <NotificationsIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography variant="h6" fontWeight={600}>
              Notifications
            </Typography>
          </Box>
          <List disablePadding>
            <ListItem>
              <ListItemText
                primary="Email Notifications"
                secondary="Receive updates and alerts via email"
              />
              <ListItemSecondaryAction>
                <Switch
                  checked={currentSettings.notifications.email}
                  onChange={() => handleToggle("email")}
                  disabled={updateMutation.isPending}
                />
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Budget Alerts"
                secondary="Get notified when approaching budget limits"
              />
              <ListItemSecondaryAction>
                <Switch
                  checked={currentSettings.notifications.budget_alerts}
                  onChange={() => handleToggle("budget_alerts")}
                  disabled={updateMutation.isPending}
                />
              </ListItemSecondaryAction>
            </ListItem>
            <ListItem>
              <ListItemText
                primary="AI Insights"
                secondary="Receive AI-powered financial insights"
              />
              <ListItemSecondaryAction>
                <Switch
                  checked={currentSettings.notifications.ai_insights}
                  onChange={() => handleToggle("ai_insights")}
                  disabled={updateMutation.isPending}
                />
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* Appearance Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <DarkModeIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography variant="h6" fontWeight={600}>
              Appearance & Preferences
            </Typography>
          </Box>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Theme</InputLabel>
              <Select
                value={currentSettings.theme}
                label="Theme"
                onChange={(e) => handleSelectChange("theme", e.target.value)}
                disabled={updateMutation.isPending}
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="system">System Default</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth size="small">
              <InputLabel>Currency</InputLabel>
              <Select
                value={currentSettings.currency}
                label="Currency"
                onChange={(e) => handleSelectChange("currency", e.target.value)}
                disabled={updateMutation.isPending}
              >
                <MenuItem value="USD">USD - US Dollar</MenuItem>
                <MenuItem value="EUR">EUR - Euro</MenuItem>
                <MenuItem value="GBP">GBP - British Pound</MenuItem>
                <MenuItem value="CAD">CAD - Canadian Dollar</MenuItem>
                <MenuItem value="AUD">AUD - Australian Dollar</MenuItem>
                <MenuItem value="JPY">JPY - Japanese Yen</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth size="small">
              <InputLabel>Timezone</InputLabel>
              <Select
                value={currentSettings.timezone}
                label="Timezone"
                onChange={(e) => handleSelectChange("timezone", e.target.value)}
                disabled={updateMutation.isPending}
              >
                <MenuItem value="UTC">UTC</MenuItem>
                <MenuItem value="America/New_York">Eastern Time (ET)</MenuItem>
                <MenuItem value="America/Chicago">Central Time (CT)</MenuItem>
                <MenuItem value="America/Denver">Mountain Time (MT)</MenuItem>
                <MenuItem value="America/Los_Angeles">Pacific Time (PT)</MenuItem>
                <MenuItem value="Europe/London">London (GMT)</MenuItem>
                <MenuItem value="Europe/Paris">Paris (CET)</MenuItem>
                <MenuItem value="Asia/Tokyo">Tokyo (JST)</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <SecurityIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography variant="h6" fontWeight={600}>
              Security
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Security settings are managed through Auth0. Click below to manage your password and security options.
          </Typography>
          <Button
            variant="outlined"
            href="https://dev-2d371r8njde648mh.us.auth0.com/u/login"
            target="_blank"
          >
            Manage Security Settings
          </Button>
        </CardContent>
      </Card>

      {/* Account Actions */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Account Actions
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <Button variant="outlined" color="error" onClick={handleLogout}>
              Sign Out
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
