import { Stack, TextField } from "@mui/material";
import CategorySelect from "../../../components/common/CategorySelect";

const formatDateForInput = (date, viewType) => {
  if (!(date instanceof Date) || isNaN(date)) return "";
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");

  if (viewType === "daily") {
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }
  return `${year}-${month}`;
};

const BudgetFilters = ({
  selectedCategory,
  setSelectedCategory,
  selectedDate,
  setSelectedDate,
  accountCreatedAt,
  viewType = "monthly",
}) => {
  const creationDate = new Date(accountCreatedAt);

  const todayDate = new Date();
  const todayStr = formatDateForInput(todayDate, viewType);
  const minDateStr = formatDateForInput(creationDate, viewType);
  const dateValue = formatDateForInput(selectedDate, viewType);

  const handleDateChange = (e) => {
    const val = e.target.value;
    if (!val) return;

    const dateString =
      viewType === "monthly" ? `${val}-01T00:00:00` : `${val}T00:00:00`;
    let newDate = new Date(dateString);

    if (newDate.getTime() < creationDate.getTime()) {
      newDate = creationDate;
    }

    if (newDate.getTime() > todayDate.getTime()) {
      newDate = todayDate;
    }

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
            backgroundColor: "grey.50",
            "&:hover": { backgroundColor: "#f9f9f9" },
            "&.Mui-focused": { backgroundColor: "#fff" },
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
