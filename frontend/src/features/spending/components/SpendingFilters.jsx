import {
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
} from "@mui/material";
import { CATEGORIES } from "../../../utils/constants";

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
    <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 4 }}>
      <FormControl sx={{ minWidth: 200 }}>
        <InputLabel>Category</InputLabel>
        <Select
          value={selectedCategory}
          label="Category"
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          <MenuItem value="All">All Categories</MenuItem>
          {CATEGORIES.map((cat) => (
            <MenuItem key={cat} value={cat}>
              {cat}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <TextField
        label="Month"
        type="month"
        fullWidth
        value={dateValue}
        onChange={handleDateChange}
        slotProps={{
          htmlInput: {
            max: today,
            min: minDate,
          },
          inputLabel: { shrink: true },
        }}
        sx={{ minWidth: 200 }}
      />
    </Stack>
  );
};

export default SpendingFilters;
