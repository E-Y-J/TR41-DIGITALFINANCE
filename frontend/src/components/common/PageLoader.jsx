import { forwardRef } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";

const PageLoader = forwardRef(({ absolute, sx, ...props }, ref) => {
  return (
    <Box
      ref={ref}
      {...props}
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: absolute ? "fixed" : "relative",
        top: 0,
        left: 0,
        width: "100%",
        height: absolute ? "100vh" : "100%",
        zIndex: 9999,
        bgcolor: "background.default",
        ...sx,
      }}
    >
      <CircularProgress size={80} thickness={4} color="primary" />
    </Box>
  );
});

export default PageLoader;
