import { Box, Typography } from "@mui/material";

/**
 * A responsive dashed preview container. Use `aspectRatio`, `minHeight`, and `maxWidth`
 * to tweak sizing at different breakpoints.
 */
export default function PreviewBox({
  label = "PREVIEW",
  children,
  aspectRatio = { xs: "4 / 3", sm: "16 / 10", md: "16 / 9" },
  minHeight = { xs: 240, sm: 300, md: 360, lg: 420 },
  maxWidth = { md: 640, lg: 760, xl: 880 },
  sx, // NEW: allow overrides
}) {
  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        mx: "auto",
        aspectRatio,
        minHeight,
        maxWidth,
        bgcolor: "background.default",
        border: "1px dashed",
        borderColor: "divider",
        borderRadius: 3,
        boxShadow: 1,
        p: { xs: 1.5, sm: 2 },
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden", // ensures contents are clipped
        ...sx, // merge caller overrides
      }}
    >
      {children ? (
        children
      ) : (
        <Typography
          variant="button"
          color="text.secondary"
          sx={{ letterSpacing: 1, textTransform: "uppercase" }}
        >
          {label}
        </Typography>
      )}
    </Box>
  );
}
