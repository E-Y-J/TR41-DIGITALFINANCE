import Stack from "@mui/material/Stack";
import MainLayout from "../layouts/MainLayout.jsx";

export default function LandingPage() {
  return (
    <MainLayout>
      <Stack spacing={2} direction="column" alignItems="center" sx={{ mt: 10 }}>
        This is the Landing Page
      </Stack>
    </MainLayout>
  );
}
