import { useState } from "react";
import {
  Box,
  Typography,
  Button,
  useTheme,
  useMediaQuery,
  alpha,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import AddTransactionModal from "./AddTransactionModal";

export const TransactionToolbar = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const theme = useTheme();

  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <Box sx={{ mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", sm: "center" },
          gap: 2,
          mb: 4,
        }}
      >
        <Box>
          <Typography
            variant={isMobile ? "h5" : "h4"}
            fontWeight={800}
            sx={{ letterSpacing: "-0.5px", color: "text.primary" }}
          >
            Transactions
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            View and manage your activity.
          </Typography>
        </Box>

        <Button
          variant="contained"
          fullWidth={isMobile}
          startIcon={<AddIcon />}
          onClick={() => setIsModalOpen(true)}
          sx={{
            borderRadius: 2.5,
            textTransform: "none",
            fontWeight: 700,
            px: 3,
            py: 1,
            fontSize: "0.95rem",
            whiteSpace: "nowrap",
            minWidth: "max-content",
            boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.25)}`,
            "&:hover": {
              boxShadow: `0 6px 16px ${alpha(theme.palette.primary.main, 0.35)}`,
            },
          }}
        >
          New Transaction
        </Button>
      </Box>

      <AddTransactionModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </Box>
  );
};

export default TransactionToolbar;
