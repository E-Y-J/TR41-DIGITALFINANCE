import { Paper, Box, Typography } from "@mui/material";

const DashboardWidget = ({ title, action, children, sx = {} }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        p: { xs: 2, sm: 3 },
        borderRadius: 4,
        border: "1px solid",
        borderColor: "grey.200",
        display: "flex",
        flexDirection: "column",
        height: "100%",
        ...sx,
      }}
    >
      {/* Header Section */}
      {(title || action) && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          {title && (
            <Typography variant="h6" fontWeight={700}>
              {title}
            </Typography>
          )}
          {action && <Box>{action}</Box>}
        </Box>
      )}

      {/* Content Section */}
      <Box sx={{ flexGrow: 1, position: "relative", overflow: "hidden" }}>
        {children}
      </Box>
    </Paper>
  );
};

export default DashboardWidget;
