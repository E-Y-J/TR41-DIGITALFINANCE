import { Box } from "@mui/material";

/**
 * Renders an image that fits inside PreviewBox. Use `fit="cover"` for edge-to-edge fill.
 */
export default function PreviewImage({ src, alt, fit = "contain" }) {
  return (
    <Box
      component="img"
      src={src}
      alt={alt}
      sx={{
        display: "block", // avoids inline-gap
        width: "100%",
        height: "100%",
        maxWidth: "100%", // extra safety
        maxHeight: "100%", // extra safety
        objectFit: fit,
        borderRadius: "inherit",
      }}
    />
  );
}
