import { Box, Stack } from "@mui/material";
import { useAiAssistantPage } from "../hooks/useAiAssistantPage";

import MobileChatHeader from "../features/chat/components/MobileChatHeader";
import ChatInputArea from "../features/chat/components/ChatInputArea";
import ChatHistoryDrawer from "../features/chat/components/ChatHistoryDrawer";
import ChatSidebar from "../features/chat/components/ChatSidebar";
import MessageList from "../features/chat/components/MessageList";

export default function AiAssistantPage() {
  const c = useAiAssistantPage();

  return (
    <Box
      sx={{
        display: "flex",
        height: "calc(100vh - 110px)",
        bgcolor: "#F8FAFC",
      }}
    >
      <ChatHistoryDrawer
        open={c.mobileHistoryOpen}
        onClose={() => c.setMobileHistoryOpen(false)}
        sidebarProps={{
          conversations: c.conversations,
          activeChatId: c.activeChatId,
          onSelectChat: (id) => {
            c.handleSelectChat(id);
            c.setMobileHistoryOpen(false);
          },
          onNewChat: () => {
            c.handleNewChat();
            c.setMobileHistoryOpen(false);
          },
          onDeleteChat: c.handleDeleteChat,
        }}
      />

      <Stack sx={{ flex: 1, minWidth: 0 }}>
        <MobileChatHeader onOpenHistory={() => c.setMobileHistoryOpen(true)} />

        <Box
          sx={{
            flexGrow: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            overflowX: "hidden",
          }}
        >
          <MessageList
            messages={c.displayMessages}
            isTyping={c.isTyping}
            messagesEndRef={c.messagesEndRef}
            onSuggestionClick={c.suggestionClickHandler}
            onSendMessage={c.handleSendMessage}
            user={c.user?.nickname || c.user?.first_name}
          />
        </Box>

        <ChatInputArea
          inputValue={c.inputValue}
          setInputValue={c.setInputValue}
          onSend={c.handleSendMessage}
        />
      </Stack>

      <Box sx={{ display: { xs: "none", md: "block" } }}>
        <ChatSidebar
          conversations={c.conversations}
          activeChatId={c.activeChatId}
          onSelectChat={c.handleSelectChat}
          onNewChat={c.handleNewChat}
          onDeleteChat={c.handleDeleteChat}
        />
      </Box>
    </Box>
  );
}
