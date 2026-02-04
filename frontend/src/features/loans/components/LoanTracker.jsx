import { useTheme, alpha } from "@mui/material/styles";
import { Box, Typography, useMediaQuery } from "@mui/material";
import { Gauge, gaugeClasses } from "@mui/x-charts/Gauge";
import EmptyState from "../../../components/common/EmptyState";

const LoanTracker = ({ loans }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const gaugeSize = isMobile ? 35 : 55;

  const getProgressColor = (value) => {
    if (value >= 75) return theme.palette.success.main;
    if (value >= 40) return theme.palette.primary.main;
    return theme.palette.warning.main;
  };

  if (!loans || loans.length === 0)
    return (
      <Box
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <EmptyState
          header="No active loans found"
          text="We couldn't find any active loans at the moment."
        />
      </Box>
    );

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: "auto",
        px: 1,
        pt: 1,
        gap: 1,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {loans.map((loan) => {
        return (
          <Box
            key={loan.id}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              p: { xs: 1.25, sm: 1.5 },
              borderRadius: 4,
              bgcolor: "background.paper",
              border: "1px solid",
              borderColor: alpha(theme.palette.grey[300], 0.5),
              boxShadow: "none",
              flexShrink: 0,
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              "&:hover": {
                borderColor: theme.palette.primary.main,
                bgcolor: alpha(theme.palette.primary.main, 0.02),
                transform: "translateY(-4px)",
                boxShadow: `
                    0 12px 24px -4px ${alpha(theme.palette.common.black, 0.08)}, 
                    0 4px 12px -2px ${alpha(theme.palette.primary.main, 0.08)}
                  `,
              },
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: { xs: 1, sm: 1.5 },
                minWidth: 0,
                flex: 1,
              }}
            >
              <Box
                sx={{
                  width: gaugeSize,
                  height: gaugeSize,
                  flexShrink: 0,
                  position: "relative",
                }}
              >
                <Gauge
                  width={gaugeSize}
                  height={gaugeSize}
                  value={loan.progress_percentage}
                  startAngle={0}
                  endAngle={360}
                  innerRadius="80%"
                  outerRadius="100%"
                  cornerRadius="50%"
                  margin={{ top: 0, bottom: 0, left: 0, right: 0 }}
                  sx={{
                    [`& .${gaugeClasses.valueText}`]: {
                      fontSize: isMobile ? 9 : 12,
                      fontWeight: 700,
                      fontFamily: theme.typography.fontFamily,
                    },
                    [`& .${gaugeClasses.valueArc}`]: {
                      fill: getProgressColor(loan.progress_percentage),
                      filter: `drop-shadow(0 0 2px ${alpha(getProgressColor(loan.progress_percentage), 0.5)})`,
                    },
                    [`& .${gaugeClasses.referenceArc}`]: {
                      fill: alpha(theme.palette.grey[200], 0.5),
                    },
                  }}
                  text={({ value }) => `${value}%`}
                />
              </Box>
              <Box sx={{ minWidth: 0 }}>
                <Typography
                  variant="body1"
                  noWrap
                  sx={{
                    fontWeight: 600,
                    lineHeight: 1.2,
                    fontSize: { xs: "0.8rem", sm: "0.9rem" },
                    color: "text.primary",
                  }}
                >
                  {loan.name}
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  noWrap
                  sx={{
                    display: "block",
                    mt: 0.5,
                    fontSize: { xs: "0.65rem", sm: "0.7rem" },
                    fontWeight: 500,
                  }}
                >
                  Orig: ${loan.original_amount.toLocaleString()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ textAlign: "right", pl: 1, flexShrink: 0 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{
                  display: "block",
                  mb: 0.5,
                  fontSize: { xs: "0.65rem", sm: "0.75rem" },
                  fontWeight: 500,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                Remaining
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  fontWeight: 800,
                  color: "text.primary",
                  lineHeight: 1,
                  fontSize: { xs: "0.9rem", sm: "1rem" },
                  whiteSpace: "nowrap",
                }}
              >
                ${loan.remaining_amount.toLocaleString()}
              </Typography>
            </Box>
          </Box>
        );
      })}
    </Box>
  );
};

export default LoanTracker;
