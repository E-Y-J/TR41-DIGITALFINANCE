import { Drawer, Box } from "@mui/material";
import ChatSidebar from "./ChatSidebar";

const ChatHistoryDrawer = ({ open, onClose, sidebarProps }) => (
  <Drawer
    anchor="bottom"
    open={open}
    onClose={onClose}
    slotProps={{
      paper: {
        sx: {
          borderTopLeftRadius: 24,
          borderTopRightRadius: 24,
          maxHeight: "70vh",
          bgcolor: "background.default",
          backgroundImage: "none",
        },
      },
    }}
  >
    <Box
      sx={{
        width: 36,
        height: 4,
        bgcolor: "divider",
        borderRadius: 10,
        mx: "auto",
        mt: 1.5,
        mb: 1,
      }}
    />
    <ChatSidebar isMobile={true} {...sidebarProps} />
  </Drawer>
);

export default ChatHistoryDrawer;
