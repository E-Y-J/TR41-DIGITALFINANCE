import { useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Avatar,
  TextField,
  Button,
  Divider,
  Grid,
  Snackbar,
  Alert,
  CircularProgress,
} from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import EmailIcon from "@mui/icons-material/Email";
import SaveIcon from "@mui/icons-material/Save";
import { useGetUser } from "../features/auth/useGetUser";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateUser } from "../api/user";
import { useAxios } from "../hooks/useAxios";

export default function ProfilePage() {
  const { data: user, isLoading } = useGetUser();
  const apiClient = useAxios();
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

  const updateMutation = useMutation({
    mutationFn: (data) => updateUser(apiClient, data),
    onSuccess: (response) => {
      // Use the PATCH response directly instead of refetching
      queryClient.setQueryData(["user"], response);
      setSnackbar({ open: true, message: "Profile updated successfully!", severity: "success" });
      setIsEditing(false);
    },
    onError: (error) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.error?.message || "Failed to update profile",
        severity: "error",
      });
    },
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  const handleCancel = () => {
    setFormData(null);
    setIsEditing(false);
  };

  const handleEdit = () => {
    setFormData({
      first_name: user?.first_name || "",
      last_name: user?.last_name || "",
      nickname: user?.nickname || "",
    });
    setIsEditing(true);
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
        My Profile
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          {/* Profile Header */}
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Avatar
              src={user?.picture_url}
              sx={{
                width: 80,
                height: 80,
                bgcolor: "primary.main",
                fontSize: "2rem",
                mr: 3,
              }}
            >
              {user?.first_name?.[0]?.toUpperCase() || <PersonIcon />}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight={600}>
                {user?.first_name} {user?.last_name}
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", color: "text.secondary", mt: 0.5 }}>
                <EmailIcon fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2">{user?.email}</Typography>
              </Box>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Profile Form */}
          <Box component="form" noValidate>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={isEditing ? formData?.first_name : user?.first_name || ""}
                  onChange={handleChange}
                  disabled={!isEditing}
                  InputProps={{ readOnly: !isEditing }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="last_name"
                  value={isEditing ? formData?.last_name : user?.last_name || ""}
                  onChange={handleChange}
                  disabled={!isEditing}
                  InputProps={{ readOnly: !isEditing }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Nickname (Display Name)"
                  name="nickname"
                  value={isEditing ? formData?.nickname : user?.nickname || ""}
                  onChange={handleChange}
                  disabled={!isEditing}
                  InputProps={{ readOnly: !isEditing }}
                  helperText="Optional display name"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  value={user?.email || ""}
                  disabled
                  InputProps={{ readOnly: true }}
                  helperText="Email is managed by Auth0 and cannot be changed here"
                />
              </Grid>
            </Grid>

            {/* Action Buttons */}
            <Box sx={{ mt: 4, display: "flex", gap: 2 }}>
              {isEditing ? (
                <>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSave}
                    disabled={updateMutation.isPending}
                  >
                    {updateMutation.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                  <Button variant="outlined" onClick={handleCancel} disabled={updateMutation.isPending}>
                    Cancel
                  </Button>
                </>
              ) : (
                <Button variant="contained" onClick={handleEdit}>
                  Edit Profile
                </Button>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Account Info Card */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Account Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Account Status
              </Typography>
              <Typography variant="body1" sx={{ textTransform: "capitalize" }}>
                {user?.account_status || "Active"}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Member Since
              </Typography>
              <Typography variant="body1">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
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
