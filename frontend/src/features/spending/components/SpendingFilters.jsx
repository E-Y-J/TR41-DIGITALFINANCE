import { Stack, TextField } from "@mui/material";
import CategorySelect from "../../../components/common/CategorySelect";

const formatMonthForInput = (date) => {
  if (!date) return "";
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
};

const SpendingFilters = ({
  selectedCategory,
  setSelectedCategory,
  selectedDate,
  setSelectedDate,
  accountCreatedAt,
}) => {
  const today = formatMonthForInput(new Date());
  const minDate = formatMonthForInput(accountCreatedAt);
  const dateValue = formatMonthForInput(selectedDate);

  const handleDateChange = (e) => {
    if (!e.target.value) return;
    const newDate = new Date(`${e.target.value}-01T00:00:00`);
    setSelectedDate(newDate);
  };

  return (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 2 }}>
      <CategorySelect
        value={selectedCategory}
        onChange={setSelectedCategory}
        sx={{ minWidth: 200 }}
      />

      <TextField
        label="Month"
        type="month"
        size="small"
        fullWidth
        value={dateValue}
        onChange={handleDateChange}
        sx={{
          minWidth: 200,
          "& .MuiOutlinedInput-root": {
            borderRadius: 3,
            backgroundColor: "grey.50",
            transition: "all 0.2s ease-in-out",
            "&:hover": {
              backgroundColor: "#f9f9f9",
              "& .MuiOutlinedInput-notchedOutline": { borderColor: "grey.400" },
            },
            "&.Mui-focused": {
              backgroundColor: "#fff",
              boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
            },
          },
        }}
        slotProps={{
          htmlInput: {
            max: today,
            min: minDate,
          },
          inputLabel: { shrink: true },
        }}
      />
    </Stack>
  );
};

export default SpendingFilters;
