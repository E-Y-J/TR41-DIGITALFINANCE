import { Stack, TextField, alpha, useTheme } from "@mui/material";
import CategorySelect from "../../../components/common/CategorySelect";
import { getLocalISODate } from "../../../utils/constants";

const BudgetFilters = ({
  selectedCategory,
  setSelectedCategory,
  selectedDate,
  setSelectedDate,
  accountCreatedAt,
  viewType = "monthly",
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  const creationDate = new Date(accountCreatedAt);
  const todayDate = new Date();

  const todayStr = getLocalISODate(todayDate, viewType);
  const minDateStr = getLocalISODate(creationDate, viewType);
  const dateValue = getLocalISODate(selectedDate, viewType);

  const handleDateChange = (e) => {
    const val = e.target.value;
    if (!val) return;
    const [year, month, day] = val.split("-").map(Number);
    let newDate = new Date(year, month - 1, day || 1);
    if (newDate.getTime() > todayDate.getTime()) newDate = todayDate;
    if (newDate.getTime() < creationDate.getTime()) newDate = creationDate;
    setSelectedDate(newDate);
  };

  return (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 2 }}>
      <CategorySelect
        value={selectedCategory}
        onChange={setSelectedCategory}
        sx={{
          minWidth: 200,
          "& .MuiOutlinedInput-root": {
            borderRadius: 3,
            bgcolor: isDarkMode
              ? alpha(theme.palette.common.black, 0.2)
              : "action.hover",
          },
        }}
      />

      <TextField
        label={viewType === "daily" ? "Select Day" : "Select Month"}
        type={viewType === "daily" ? "date" : "month"}
        size="small"
        fullWidth
        value={dateValue}
        onChange={handleDateChange}
        sx={{
          minWidth: 200,
          "& .MuiOutlinedInput-root": {
            borderRadius: 3,
            backgroundColor: isDarkMode
              ? alpha(theme.palette.common.black, 0.2)
              : "action.hover",
            transition: theme.transitions.create([
              "background-color",
              "box-shadow",
            ]),

            "&:hover": {
              backgroundColor: isDarkMode
                ? alpha(theme.palette.common.black, 0.3)
                : "action.selected",
            },
            "&.Mui-focused": {
              backgroundColor: "background.paper",
              boxShadow: `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`,
            },
            "& input::-webkit-calendar-picker-indicator": {
              filter: isDarkMode ? "invert(1) brightness(0.9)" : "none",
              cursor: "pointer",
            },
          },
          "& .MuiInputLabel-root": {
            fontWeight: 600,
            color: "text.secondary",
            "&.Mui-focused": { color: "primary.main" },
          },
        }}
        slotProps={{
          htmlInput: {
            max: todayStr,
            min: minDateStr,
          },
          inputLabel: { shrink: true },
        }}
      />
    </Stack>
  );
};

export default BudgetFilters;
