import { Box, Stack } from "@mui/material";
import MainLayout from "../layouts/MainLayout.jsx";
import Hero from "../features/landing/Hero";
import FeaturesGrid from "../features/landing/FeaturesGrid";
import ProblemStatement from "../features/landing/ProblemStatement";

const LandingPage = () => {
  return (
    <MainLayout>
      <Stack spacing={10}>
        <Box id="hero">
          <Hero />
        </Box>
        <Box id="about">
          <ProblemStatement />
        </Box>
        <Box id="features">
          <FeaturesGrid />
        </Box>
      </Stack>
    </MainLayout>
  );
};

export default LandingPage;
