import CircularProgress, {
  circularProgressClasses,
} from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

const mock = [
  { id: 1, name: "Student Loan", amount: 14999.0, left: 12000.0 },
  { id: 2, name: "Car Loan", amount: 20000.0, left: 15000.0 },
  { id: 3, name: "Personal Loan", amount: 5000.0, left: 2500.0 },
  { id: 4, name: "Home Loan", amount: 300000.0, left: 280000.0 },
  { id: 5, name: "Credit Card Debt", amount: 10000.0, left: 1000.0 },
];

const test = [];

const getProgressColor = (value) => {
  if (value >= 75) return "success";
  if (value >= 40) return "primary";
  return "warning";
};

function CircularProgressWithLabel({ value }) {
  const color = getProgressColor(value);

  return (
    <Box sx={{ position: "relative", display: "inline-flex" }}>
      <CircularProgress
        variant="determinate"
        sx={{
          color: (theme) => theme.palette.grey[200],
        }}
        size={50}
        thickness={4}
        value={100}
      />

      <CircularProgress
        variant="determinate"
        color={color}
        sx={{
          position: "absolute",
          left: 0,
          [`& .${circularProgressClasses.circle}`]: {
            strokeLinecap: "round",
          },
        }}
        size={50}
        thickness={4}
        value={value}
      />

      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: "absolute",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Typography
          variant="caption"
          component="div"
          fontWeight={700}
          color="text.secondary"
          sx={{ fontSize: "0.75rem" }}
        >
          {`${Math.round(value)}%`}
        </Typography>
      </Box>
    </Box>
  );
}

const LoanTracker = () => {
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
          const percentagePaid =
            ((loan.amount - loan.left) / loan.amount) * 100;

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
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <CircularProgressWithLabel value={percentagePaid} />

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
