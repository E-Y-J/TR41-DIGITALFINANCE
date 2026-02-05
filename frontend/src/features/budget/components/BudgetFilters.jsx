import { Stack, TextField } from "@mui/material";
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

    if (newDate.getTime() > todayDate.getTime()) {
      newDate = todayDate;
    }

    if (newDate.getTime() < creationDate.getTime()) {
      newDate = creationDate;
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
