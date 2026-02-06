import { Box, Typography, Paper, CircularProgress, Fade } from "@mui/material";
import SpendingFilters from "./BudgetFilters";
import MonthlyLineChart from "./MonthlyLineChart";
import EmptyTrendView from "../../../components/common/EmptyTrendView";
import { formatDate } from "../../../utils/constants";

const ViewMonthly = ({
  selectedCategory,
  setSelectedCategory,
  selectedDate,
  setSelectedDate,
  accountCreatedAt,
  chartData,
  isLoading,
  isFetching,
}) => {
  const headerDate = formatDate(selectedDate, "monthly");
  return (
    <Paper
      elevation={3}
      sx={{
        p: { xs: 2, sm: 3 },
        borderRadius: 4,
        border: "1px solid",
        borderColor: "grey.200",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box
        sx={{
          mb: 3,
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          alignItems: { xs: "flex-start", md: "center" },
          justifyContent: "space-between",
          gap: 2,
        }}
      >
        <Box>
          <Typography
            variant="h6"
            component="h2"
            fontWeight={700}
            lineHeight={1.2}
          >
            {selectedDate
              ? `Monthly Spending Since: ${headerDate}`
              : "Monthly Trend Analysis"}
          </Typography>
        </Box>

        <Box sx={{ width: { xs: "100%", md: "auto" } }}>
          <SpendingFilters
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            selectedDate={selectedDate}
            setSelectedDate={setSelectedDate}
            accountCreatedAt={accountCreatedAt}
            viewType="monthly"
          />
        </Box>
      </Box>

      {!selectedDate ? (
        <EmptyTrendView
          header="Visualize Your Spending Trend"
          text="Pick a starting point to see how your habits evolved."
        />
      ) : isLoading ? (
        <Box sx={{ p: 6, textAlign: "center" }}>
          <CircularProgress size={40} />
        </Box>
      ) : (
        <Fade in={!!selectedDate} timeout={500}>
          <Box
            sx={{
              position: "relative",
              opacity: isFetching ? 0.4 : 1,
              transition: "opacity 0.2s ease",
              pointerEvents: isFetching ? "none" : "auto",
            }}
          >
            {isFetching && (
              <CircularProgress
                size={20}
                sx={{
                  position: "absolute",
                  top: 10,
                  right: 10,
                  zIndex: 1,
                }}
              />
            )}

            <MonthlyLineChart selectedDate={selectedDate} data={chartData} />
          </Box>
        </Fade>
      )}
    </Paper>
  );
};

export default ViewMonthly;
