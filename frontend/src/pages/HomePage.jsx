import { Grid, Paper, Typography } from "@mui/material";
import DashboardLayout from "../layouts/DashboardLayout";

const HomePage = () => {
  return (
    <DashboardLayout>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Dashboard Overview (*Placeholder Content*)
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{ p: 3, display: "flex", flexDirection: "column", height: 140 }}
          >
            <Typography color="textSecondary" gutterBottom>
              Total Balance
            </Typography>
            <Typography variant="h4">$12,450.00</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{ p: 3, display: "flex", flexDirection: "column", height: 140 }}
          >
            <Typography color="textSecondary" gutterBottom>
              Monthly Income
            </Typography>
            <Typography variant="h4" sx={{ color: "green" }}>
              +$3,200.00
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{ p: 3, display: "flex", flexDirection: "column", height: 140 }}
          >
            <Typography color="textSecondary" gutterBottom>
              Monthly Expenses
            </Typography>
            <Typography variant="h4" sx={{ color: "red" }}>
              -$1,150.00
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default HomePage;
