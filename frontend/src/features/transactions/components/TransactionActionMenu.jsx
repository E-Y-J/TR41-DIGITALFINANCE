import {
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
  alpha,
  useTheme,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

const TransactionActionMenu = ({
  contextMenu,
  onClose,
  selectedRow,
  onEdit,
  onDelete,
}) => {
  const theme = useTheme();

  const handleAction = (actionCallback) => {
    if (actionCallback) actionCallback(selectedRow);
    onClose();
  };

  return (
    <Menu
      open={contextMenu !== null}
      onClose={onClose}
      anchorReference="anchorPosition"
      anchorPosition={
        contextMenu !== null
          ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
          : undefined
      }
      transformOrigin={{ vertical: "top", horizontal: "left" }}
      slotProps={{
        paper: {
          elevation: 0,
          sx: {
            minWidth: 200,
            borderRadius: 3,
            border: `1px solid ${theme.palette.divider}`,
            boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.08)",
            overflow: "visible",
            mt: 1.5,
          },
        },
      }}
    >
      <Box
        sx={{ px: 2.5, py: 1.5, bgcolor: alpha(theme.palette.grey[50], 0.5) }}
      >
        <Typography
          variant="caption"
          display="block"
          sx={{
            fontWeight: 700,
            color: "text.disabled",
            fontSize: "0.65rem",
            letterSpacing: 1,
            mb: 0.5,
          }}
        >
          MANAGE TRANSACTION
        </Typography>
        <Typography
          variant="subtitle2"
          noWrap
          sx={{
            fontWeight: 600,
            color: "text.primary",
            maxWidth: 180,
          }}
        >
          {selectedRow?.merchant_name || "Select Action"}
        </Typography>
      </Box>

      <Divider />

      <MenuItem
        onClick={() => handleAction(onEdit)}
        sx={{
          mx: 1,
          mt: 1,
          borderRadius: 1.5,
          "&:hover": {
            bgcolor: alpha(theme.palette.primary.main, 0.08),
            "& .MuiListItemIcon-root": { color: "primary.main" },
          },
        }}
      >
        <ListItemIcon sx={{ minWidth: 32, color: "text.secondary" }}>
          <EditIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText
          primary="Edit Details"
          primaryTypographyProps={{ variant: "body2", fontWeight: 500 }}
        />
      </MenuItem>

      <MenuItem
        onClick={() => handleAction(onDelete)}
        sx={{
          mx: 1,
          my: 0.5,
          mb: 1,
          borderRadius: 1.5,
          color: "error.main",
          "&:hover": {
            bgcolor: alpha(theme.palette.error.main, 0.08),
          },
        }}
      >
        <ListItemIcon sx={{ minWidth: 32, color: "error.main" }}>
          <DeleteIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText
          primary="Delete"
          primaryTypographyProps={{ variant: "body2", fontWeight: 600 }}
        />
      </MenuItem>
    </Menu>
  );
};

export default TransactionActionMenu;
