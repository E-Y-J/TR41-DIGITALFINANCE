import { forwardRef } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";

const PageLoader = forwardRef((props, ref) => {
  return (
    <Box
      ref={ref}
      {...props}
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: props.absolute ? "fixed" : "relative",
        top: 0,
        left: 0,
        width: "100%",
        height: props.absolute ? "100vh" : "100%",
        zIndex: 9999,
        bgcolor: "background.default",
        ...props.sx,
      }}
    >
      <CircularProgress size={80} thickness={4} color="primary" />
    </Box>
  );
});

export default PageLoader;
