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
          bgcolor: "#F8FAFC",
          backgroundImage: "none",
        },
      },
    }}
  >
    <Box
      sx={{
        width: 36,
        height: 4,
        bgcolor: "grey.400",
        borderRadius: 10,
        mx: "auto",
        mt: 1.5,
        mb: 1,
        opacity: 0.6,
      }}
    />
    <ChatSidebar isMobile={true} {...sidebarProps} />
  </Drawer>
);

export default ChatHistoryDrawer;
