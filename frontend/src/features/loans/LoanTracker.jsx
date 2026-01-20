import { useTheme } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { Gauge, gaugeClasses } from "@mui/x-charts/Gauge";

const mock = [
  { id: 1, name: "Student Loan", amount: 14999.0, left: 12000.0 },
  { id: 2, name: "Car Loan", amount: 20000.0, left: 15000.0 },
  { id: 3, name: "Personal Loan", amount: 5000.0, left: 2500.0 },
  { id: 4, name: "Home Loan", amount: 300000.0, left: 280000.0 },
  { id: 5, name: "Credit Card Debt", amount: 10000.0, left: 1000.0 },
];

const LoanTracker = () => {
  const theme = useTheme();

  const getProgressColor = (value) => {
    if (value >= 75) return theme.palette.success.main;
    if (value >= 40) return theme.palette.primary.main;
    return theme.palette.warning.main;
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        justifyContent: "flex-start",
        width: "100%",
      }}
    >
      {mock && mock.length > 0 ? (
        mock.map((loan) => {
          const percentagePaid = Math.round(
            ((loan.amount - loan.left) / loan.amount) * 100,
          );

          return (
            <Box
              key={loan.id}
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                py: 1.25,
                borderBottom: "1px solid",
                borderColor: "divider",
                "&:last-child": {
                  borderBottom: "none",
                  pb: 0,
                },
                "&:first-of-type": {
                  pt: 0,
                },
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "start",
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    width: 55,
                    height: 55,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Gauge
                    width={55}
                    height={55}
                    value={percentagePaid}
                    startAngle={0}
                    endAngle={360}
                    innerRadius="75%"
                    outerRadius="100%"
                    cornerRadius="50%"
                    margin={{ top: 0, bottom: 0, left: 0, right: 0 }}
                    sx={{
                      [`& .${gaugeClasses.valueText}`]: {
                        fontSize: 13,
                        fontWeight: 700,
                        transform: "translate(0px, 0px)",
                      },
                      [`& .${gaugeClasses.valueArc}`]: {
                        fill: getProgressColor(percentagePaid),
                      },
                    }}
                    text={({ value }) => `${value}%`}
                  />
                </Box>

                <Box>
                  <Typography variant="body1" fontWeight={600}>
                    {loan.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Original: ${loan.amount.toLocaleString()}
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ textAlign: "right" }}>
                <Typography variant="body2" color="text.secondary">
                  Remaining
                </Typography>
                <Typography
                  variant="body1"
                  fontWeight={700}
                  color="text.primary"
                >
                  ${loan.left.toLocaleString()}
                </Typography>
              </Box>
            </Box>
          );
        })
      ) : (
        <Box
          sx={{
            py: 4,
            textAlign: "center",
            bgcolor: "grey.50",
            borderRadius: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            No active loans found.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default LoanTracker;
