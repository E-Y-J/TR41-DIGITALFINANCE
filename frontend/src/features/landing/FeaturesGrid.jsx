import {
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Container,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PreviewBox from "../../components/PreviewBox";
import PreviewImage from "../../components/PreviewImage";


const FEATURES = [
  {
    title: "Transaction Management",
    desc: "Enter income and expenses manually or import directly from e-wallets like PayPal. Every entry captures amount, type, date, and category.",
    icon: <AccountBalanceWalletIcon color="primary" />,
    points: ["Manual & Auto Import", "PayPal Integration", "Detailed Metadata"],
    image: "/transaction.png", 
  },
  {
    title: "AI Categorization",
    desc: "Our AI analyzes your spending patterns to predict and assign categories to new transactions automatically, reducing manual bookkeeping.",
    icon: <AutoAwesomeIcon color="secondary" />,
    points: ["Pattern Recognition", "Auto-labeling", "Smart Insights"],
    image: "/daily_trend.png",
  },
  {
    title: "Unified Dashboard",
    desc: "A single source of truth for your finances. Monitor balances, monthly totals, and category breakdowns in real-time.",
    icon: <DashboardIcon color="primary" />,
    points: ["Real-time Balances", "Spending Trends", "Category Breakdown"],
    image: "/trend.png", 
  },
];

const FeaturesGrid = () => {
  return (
    <Box
      id="features"
      sx={{ bgcolor: "background.default", py: { xs: 8, md: 15 } }}
    >
      <Container maxWidth="lg">
        <Stack spacing={12}>
          {FEATURES.map((feature, index) => (
            <Grid
              container
              spacing={{ xs: 4, md: 10 }}
              alignItems="center"
              key={feature.title}
              direction={index % 2 === 0 ? "row" : "row-reverse"}
              sx={{ minHeight: "60vh" }}
            >
              <Grid item xs={12} md={6}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    mb: 2,
                    gap: 1.5,
                  }}
                >
                  {feature.icon}
                  <Typography
                    variant="overline"
                    fontWeight={700}
                    color="text.secondary"
                  >
                    Feature {index + 1}
                  </Typography>
                </Box>

                <Typography variant="h3" fontWeight={800} gutterBottom>
                  {feature.title}
                </Typography>

                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ mb: 4, fontSize: "1.1rem" }}
                >
                  {feature.desc}
                </Typography>

                <List>
                  {feature.points.map((point) => (
                    <ListItem key={point} disableGutters sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckCircleOutlineIcon
                          fontSize="small"
                          color="secondary"
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={point}
                        slotProps={{ primary: { fontWeight: 500 } }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>

              <Grid item xs={12} md={6}>
                {/* Preview panel: modeled after Hero, slightly smaller */}
                <Box
                  sx={{
                    width: "100%",
                    height: { xs: "auto", md: 480 }, // Hero uses 550; a bit smaller here
                    borderRadius: 4,
                    bgcolor: "background.paper",
                    border: "1px solid",
                    borderColor: "divider",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    position: "relative",
                    boxShadow: "0 20px 50px rgba(2, 6, 23, 0.08)",
                    p: { xs: 1.5, md: 3 },
                    overflow: "hidden",
                  }}
                >
                  <PreviewBox
                    label={`Preview: ${feature.title}`}
                    // Match Hero’s approach: ratio on small screens; fill panel on md+
                    aspectRatio={{ xs: "16 / 9", md: "16 / 9" }}
                    minHeight={{ xs: 240, md: 360 }}
                    maxWidth="100%"
                    sx={{ p: 0, width: "100%", height: "100%" }}
                  >
                    {feature.image ? (
                      <PreviewImage
                        src={feature.image}
                        alt={`${feature.title} preview`}
                        fit="contain" // consistent with Hero to avoid cropping on small screens
                      />
                    ) : null}
                  </PreviewBox>
                </Box>
              </Grid>
            </Grid>
          ))}
        </Stack>
      </Container>
    </Box>
  );
};

export default FeaturesGrid;
