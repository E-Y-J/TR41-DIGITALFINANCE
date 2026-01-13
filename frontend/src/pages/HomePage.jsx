import { Grid, Paper, Typography, Button } from "@mui/material";
import DashboardLayout from "../layouts/DashboardLayout";
import { useTest } from "../hooks/queries/useTest";
import { useAxios } from "../hooks/useAxios";

export default function HomePage() {
  const apiClient = useAxios();
  const { data: msg, isLoading, isError } = useTest();

  // if (isLoading) return <div>Loading...</div>;
  // if (isError) return <div>Failed to load transactions.</div>;
  const getAuthorizedData = async () => {
    try {
      const response = await apiClient.get("/test/protected-endpoint");
      console.log("Authorized data:", response.data);
    } catch (error) {
      console.error("Error fetching authorized data:", error);
    }
  };
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
            run
            <Typography variant="h4">$12,450.00</Typography>
          </Paper>
        </Grid>
        <Paper>
          <Typography variant="h6">
            {isLoading
              ? "Loading..."
              : isError
              ? "Error loading message"
              : msg?.message}
          </Typography>
        </Paper>
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
          <Button onClick={getAuthorizedData}>
            Testing backend connection
          </Button>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
}
