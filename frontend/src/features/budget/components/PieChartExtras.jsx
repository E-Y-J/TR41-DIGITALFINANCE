import { Box, Stack, Typography, styled } from "@mui/material";
import { useDrawingArea } from "@mui/x-charts/hooks";
import { getCategoryColor } from "../../../utils/constants";

const StyledText = styled("text")(({ theme }) => ({
  fill: theme.palette.text.primary,
  textAnchor: "middle",
  dominantBaseline: "central",
  fontWeight: "bold",
}));

export function PieCenterLabel({ children, primary }) {
  const { width, height, left, top } = useDrawingArea();
  return (
    <>
      <StyledText
        x={left + width / 2}
        y={top + height / 2 - 10}
        style={{ fontSize: 22 }}
      >
        {primary}
      </StyledText>
      <StyledText
        x={left + width / 2}
        y={top + height / 2 + 15}
        style={{ fontSize: 12, fill: "#666" }}
      >
        {children}
      </StyledText>
    </>
  );
}

export const CustomLegend = ({ data }) => {
  const legendItems = data.filter((item) => item.isSpent);

  return (
    <Stack
      direction="row"
      flexWrap="wrap"
      justifyContent="center"
      gap={2}
      sx={{
        my: 1,
        px: 1,
        display: "flex",
      }}
    >
      {legendItems.map((item) => (
        <Stack key={item.id} direction="row" alignItems="center" gap={1}>
          <Box
            sx={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              bgcolor: getCategoryColor(item.label),
            }}
          />
          <Typography
            variant="caption"
            fontWeight={600}
            color="text.secondary"
            sx={{ whiteSpace: "nowrap" }}
          >
            {item.label}
          </Typography>
        </Stack>
      ))}
    </Stack>
  );
};
