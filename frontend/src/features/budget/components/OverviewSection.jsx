import React from "react";
import {
  Box,
  Typography,
  Stack,
  alpha,
  useTheme,
  Paper,
  Divider,
  Grid,
} from "@mui/material";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";

const OverviewSection = ({ budget, meta }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  const spent = parseFloat(budget.spent || 0);
  const amount = parseFloat(budget.amount || 0);
  const usage = budget.percentage_used || 0;

  return (
    <Box sx={{ mb: 1.5 }}>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{
          mb: 1,
          fontWeight: 800,
          textTransform: "uppercase",
          display: "block",
          letterSpacing: 1.2,
          px: 0.5,
        }}
      >
        {budget.period || "Monthly"} Overview
      </Typography>

      <Paper
        variant="outlined"
        sx={{
          p: { xs: 2, sm: "16px 24px" },
          borderRadius: 4,
          bgcolor: isDarkMode
            ? alpha(theme.palette.background.paper, 0.4)
            : "background.paper",
          borderColor: "divider",
          backgroundImage: "none",
        }}
      >
        <Stack
          // Transitions from vertical on mobile to horizontal on deskto
          direction={{ xs: "column", md: "row" }}
          spacing={{ xs: 2.5, md: 0 }}
          alignItems={{ xs: "flex-start", md: "center" }}
          justifyContent="space-between"
          sx={{ width: "100%" }}
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <Box
              sx={{
                width: { xs: 40, md: 44 },
                height: { xs: 40, md: 44 },
                borderRadius: "12px",
                bgcolor: alpha(theme.palette.primary.main, 0.12),
                color: "primary.main",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <AccountBalanceWalletIcon
                sx={{ fontSize: { xs: "1.2rem", md: "1.4rem" } }}
              />
            </Box>
            <Box>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={800}
                sx={{ display: "block", mb: -0.2, fontSize: "0.65rem" }}
              >
                OVERALL SPENT
              </Typography>
              <Stack direction="row" alignItems="baseline" spacing={0.75}>
                <Typography
                  variant="h5"
                  fontWeight={900}
                  sx={{ letterSpacing: "-0.5px" }}
                >
                  $
                  {spent.toLocaleString(undefined, {
                    maximumFractionDigits: 0,
                  })}
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  fontWeight={600}
                  sx={{ opacity: 0.8 }}
                >
                  / $
                  {amount.toLocaleString(undefined, {
                    maximumFractionDigits: 0,
                  })}
                </Typography>
              </Stack>
            </Box>
          </Stack>

          <Box sx={{ width: { xs: "100%", md: "auto" } }}>
            <Grid
              container
              spacing={1}
              sx={{
                "& .MuiDivider-root": { display: { xs: "none", md: "block" } },
                alignItems: "center",
              }}
            >
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                sx={{ width: "100%" }}
                spacing={2}
                divider={
                  <Divider
                    orientation="vertical"
                    flexItem
                    sx={{ height: 24, alignSelf: "center", opacity: 0.3 }}
                  />
                }
              >
                <Box
                  sx={{
                    textAlign: { xs: "left", md: "center" },
                    minWidth: { xs: "auto", md: 70 },
                  }}
                >
                  <Typography
                    variant="caption"
                    color="success.main"
                    fontWeight={800}
                    display="block"
                    sx={{ fontSize: "0.65rem" }}
                  >
                    HEALTHY
                  </Typography>
                  <Typography variant="subtitle2" fontWeight={900}>
                    {meta.healthy_count}
                  </Typography>
                </Box>

                <Box
                  sx={{
                    textAlign: { xs: "left", md: "center" },
                    minWidth: { xs: "auto", md: 70 },
                  }}
                >
                  <Typography
                    variant="caption"
                    color="warning.main"
                    fontWeight={800}
                    display="block"
                    sx={{ fontSize: "0.65rem" }}
                  >
                    WARNING
                  </Typography>
                  <Typography variant="subtitle2" fontWeight={900}>
                    {meta.warning_count}
                  </Typography>
                </Box>

                <Box
                  sx={{
                    textAlign: { xs: "left", md: "center" },
                    minWidth: { xs: "auto", md: 70 },
                  }}
                >
                  <Typography
                    variant="caption"
                    color="error.main"
                    fontWeight={800}
                    display="block"
                    sx={{ fontSize: "0.65rem" }}
                  >
                    CRITICAL
                  </Typography>
                  <Typography
                    variant="subtitle2"
                    fontWeight={900}
                    color="error.main"
                  >
                    {meta.exceeded_count}
                  </Typography>
                </Box>

                <Box sx={{ textAlign: "right", pl: { md: 2 } }}>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    fontWeight={800}
                    display="block"
                    sx={{ fontSize: "0.65rem" }}
                  >
                    USAGE
                  </Typography>
                  <Typography
                    variant="h6"
                    fontWeight={900}
                    color={usage >= 100 ? "error.main" : "text.primary"}
                    sx={{ lineHeight: 1 }}
                  >
                    {Math.round(usage)}%
                  </Typography>
                </Box>
              </Stack>
            </Grid>
          </Box>
        </Stack>
      </Paper>
    </Box>
  );
};

export default OverviewSection;
