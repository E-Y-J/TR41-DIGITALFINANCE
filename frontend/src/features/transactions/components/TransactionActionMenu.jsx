import { Menu, MenuItem, ListItemIcon, Box, Typography } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

const TransactionActionMenu = ({
  contextMenu,
  onClose,
  selectedRow,
  onEdit,
  onDelete,
}) => {
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
      slotProps={{
        paper: {
          elevation: 3,
          sx: {
            borderRadius: 2,
            minWidth: 180,
            overflow: "visible",
            filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
            mt: 0,
          },
        },
      }}
    >
      <Box
        sx={{
          px: 2,
          py: 1.5,
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: "grey.50",
          outline: "none",
        }}
      >
        <Typography
          variant="caption"
          display="block"
          color="text.secondary"
          fontWeight={700}
          sx={{ fontSize: "0.7rem", letterSpacing: "0.5px" }}
        >
          MANAGE
        </Typography>
        <Typography
          variant="body2"
          fontWeight={600}
          noWrap
          sx={{ maxWidth: 200 }}
        >
          {selectedRow?.merchant_name || "Transaction"}
        </Typography>
      </Box>

      <MenuItem
        onClick={() => {
          if (onEdit) onEdit(selectedRow);
          onClose();
        }}
        dense
        sx={{ py: 1, mt: 0.5 }}
      >
        <ListItemIcon>
          <EditIcon fontSize="small" />
        </ListItemIcon>
        Edit
      </MenuItem>

      <MenuItem
        onClick={() => {
          if (onDelete) onDelete(selectedRow);
          onClose();
        }}
        dense
        sx={{ color: "error.main", py: 1 }}
      >
        <ListItemIcon>
          <DeleteIcon fontSize="small" color="error" />
        </ListItemIcon>
        Delete
      </MenuItem>
    </Menu>
  );
};

export default TransactionActionMenu;
