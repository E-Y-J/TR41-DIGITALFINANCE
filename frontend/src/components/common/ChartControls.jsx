import { Stack, IconButton, Typography } from "@mui/material";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";

const ChartControls = ({ page, totalPages, onPrev, onNext, sx }) => (
  <Stack
    direction="row"
    alignItems="center"
    justifyContent="center"
    gap={2}
    sx={{ mt: 1, ...sx }}
  >
    <IconButton
      onClick={onPrev}
      size="small"
      sx={{ border: "1px solid", borderColor: "divider" }}
    >
      <NavigateBeforeIcon />
    </IconButton>

    <Typography variant="caption" fontWeight={600} color="text.secondary">
      {page + 1} / {totalPages}
    </Typography>

    <IconButton
      onClick={onNext}
      size="small"
      sx={{ border: "1px solid", borderColor: "divider" }}
    >
      <NavigateNextIcon />
    </IconButton>
  </Stack>
);

export default ChartControls;
