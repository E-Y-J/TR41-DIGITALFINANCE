import {
  Stack,
  Box,
  Typography,
  Tooltip,
  Chip,
  IconButton,
  Button,
  alpha,
  useTheme,
} from "@mui/material";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import ViewModuleIcon from "@mui/icons-material/ViewModule";
import ViewListIcon from "@mui/icons-material/ViewList";
import AddIcon from "@mui/icons-material/Add";

const BudgetHeader = ({ meta, viewMode, setViewMode, isMobile, onAdd }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      justifyContent="space-between"
      alignItems={{ xs: "flex-start", sm: "center" }}
      spacing={{ xs: 3, sm: 2 }}
      sx={{ mb: { xs: 4, sm: 6 }, px: 0.5 }}
    >
      <Stack direction="row" spacing={2.5} alignItems="center">
        <Box
          sx={{
            p: { xs: 1, sm: 1.2 },
            borderRadius: "14px",
            bgcolor: alpha(theme.palette.primary.main, 0.12),
            color: "primary.main",
            display: "flex",
            boxShadow: `inset 0 0 0 1px ${alpha(theme.palette.primary.main, 0.1)}`,
          }}
        >
          <AccountBalanceWalletIcon sx={{ fontSize: { xs: 22, sm: 26 } }} />
        </Box>

        <Box>
          <Typography
            variant={isMobile ? "h6" : "h5"}
            fontWeight={900}
            sx={{ letterSpacing: "-0.02em" }}
          >
            My Budgets
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
            {meta.warning_count > 0 && (
              <Tooltip
                title={`${meta.warning_count} near limit`}
                arrow
                placement="top"
              >
                <Chip
                  label={`${meta.warning_count} Warning`}
                  size="small"
                  sx={{
                    fontWeight: 800,
                    borderRadius: "6px",
                    bgcolor: alpha(theme.palette.warning.main, 0.15),
                    color: isDarkMode ? "warning.light" : "warning.main",
                    fontSize: "0.65rem",
                    border: "none",
                    cursor: "help",
                  }}
                />
              </Tooltip>
            )}
            {meta.exceeded_count > 0 && (
              <Tooltip
                title={`${meta.exceeded_count} exceeded`}
                arrow
                placement="top"
              >
                <Chip
                  label={`${meta.exceeded_count} Critical`}
                  size="small"
                  sx={{
                    fontWeight: 800,
                    borderRadius: "6px",
                    bgcolor: alpha(theme.palette.error.main, 0.15),
                    color: isDarkMode ? "error.light" : "error.main",
                    fontSize: "0.65rem",
                    border: "none",
                    cursor: "help",
                  }}
                />
              </Tooltip>
            )}
          </Stack>
        </Box>
      </Stack>

      <Stack
        direction="row"
        spacing={2}
        alignItems="center"
        width={{ xs: "100%", sm: "auto" }}
        justifyContent={{ xs: "space-between", sm: "flex-end" }}
      >
        {!isMobile && (
          <Box
            sx={{
              display: "flex",
              p: 0.6,
              borderRadius: "12px",
              bgcolor: isDarkMode
                ? alpha(theme.palette.common.white, 0.05)
                : alpha(theme.palette.common.black, 0.05),
              border: `1px solid ${theme.palette.divider}`,
            }}
          >
            <Tooltip title="Grid View" arrow>
              <IconButton
                size="small"
                onClick={() => setViewMode("grid")}
                sx={{
                  p: 1,
                  borderRadius: "9px",
                  bgcolor:
                    viewMode === "grid" ? "background.paper" : "transparent",
                  color:
                    viewMode === "grid" ? "primary.main" : "text.secondary",
                  boxShadow: viewMode === "grid" ? theme.shadows[2] : "none",
                  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
              >
                <ViewModuleIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="List View" arrow>
              <IconButton
                size="small"
                onClick={() => setViewMode("list")}
                sx={{
                  p: 1,
                  borderRadius: "9px",
                  bgcolor:
                    viewMode === "list" ? "background.paper" : "transparent",
                  color:
                    viewMode === "list" ? "primary.main" : "text.secondary",
                  boxShadow: viewMode === "list" ? theme.shadows[2] : "none",
                  transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
              >
                <ViewListIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        )}

        <Button
          variant="contained"
          disableElevation
          fullWidth={isMobile}
          startIcon={<AddIcon />}
          onClick={onAdd}
          sx={{
            height: 44,
            borderRadius: "12px",
            px: { xs: 2, sm: 3.5 },
            fontWeight: 800,
            textTransform: "none",
            fontSize: { xs: "0.85rem", sm: "0.95rem" },
            boxShadow: isDarkMode
              ? `0 8px 16px ${alpha(theme.palette.primary.main, 0.25)}`
              : theme.shadows[4],
          }}
        >
          {isMobile ? "Add Budget" : "New Budget"}
        </Button>
      </Stack>
    </Stack>
  );
};

export default BudgetHeader;
