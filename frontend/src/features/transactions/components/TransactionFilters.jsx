import {
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Box,
  Button,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import MoneyOffIcon from "@mui/icons-material/MoneyOff";
import AppsIcon from "@mui/icons-material/Apps";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";

import CategorySelect from "../../../components/common/CategorySelect";

const getButtonStyle = (isActive) => ({
  textTransform: "none",
  fontWeight: 600,
  borderRadius: "10px",
  px: 2,
  py: 0.5,
  minWidth: "fit-content",
  whiteSpace: "nowrap",
  color: isActive ? "common.white" : "text.secondary",
  bgcolor: isActive ? "primary.main" : "background.paper",
  border: "1px solid",
  borderColor: isActive ? "primary.main" : "divider",
  boxShadow: isActive ? "0 2px 8px rgba(25, 118, 210, 0.25)" : "none",
  "&:hover": {
    bgcolor: isActive ? "primary.dark" : "action.hover",
    borderColor: isActive ? "primary.dark" : "grey.400",
  },
});

const textFieldStyles = {
  flex: 1,
  "& .MuiOutlinedInput-root": {
    borderRadius: 3,
    backgroundColor: "background.paper",
    "& fieldset": { borderColor: "divider" },
    "&:hover fieldset": { borderColor: "grey.400" },
  },
};

const TransactionFilters = ({ filters, onFilterChange }) => {
  const handleChange = (field, value) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const handleReset = () => {
    onFilterChange({
      search: "",
      category: "All",
      type: "All",
      sort_by: "date",
      sort_order: "desc",
    });
  };

  const toggleDateSort = () => {
    const nextOrder = filters.sort_order === "asc" ? "desc" : "asc";
    handleChange("sort_order", nextOrder);
  };

  const hasActiveFilters =
    filters.search?.trim() !== "" ||
    (filters.category !== "All" && filters.category !== "") ||
    (filters.type !== "All" && filters.type !== "") ||
    filters.sort_order === "asc";

  return (
    <Box
      sx={{ display: "flex", flexDirection: "column", gap: 2, width: "100%" }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          gap: 1.5,
          width: "100%",
        }}
      >
        <TextField
          placeholder="Search merchant..."
          size="small"
          value={filters.search}
          onChange={(e) => handleChange("search", e.target.value)}
          sx={textFieldStyles}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" fontSize="small" />
                </InputAdornment>
              ),
            },
          }}
        />

        <CategorySelect
          value={filters.category}
          onChange={(val) => handleChange("category", val)}
          sx={{
            minWidth: { xs: "100%", sm: 200 },
          }}
        />
      </Box>

      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", md: "center" },
          gap: 2,
        }}
      >
        <Box
          sx={{
            display: "flex",
            gap: 1,
            width: { xs: "100%", sm: "auto" },
            overflowX: "auto",
            pb: { xs: 0.5, sm: 0 },
            "&::-webkit-scrollbar": { display: "none" },
          }}
        >
          <Button
            startIcon={<AppsIcon />}
            onClick={() => handleChange("type", "All")}
            sx={getButtonStyle(filters.type === "All" || !filters.type)}
          >
            All
          </Button>
          <Button
            startIcon={<AttachMoneyIcon />}
            onClick={() => handleChange("type", "income")}
            sx={getButtonStyle(filters.type === "income")}
          >
            Income
          </Button>
          <Button
            startIcon={<MoneyOffIcon />}
            onClick={() => handleChange("type", "expense")}
            sx={getButtonStyle(filters.type === "expense")}
          >
            Expense
          </Button>
        </Box>

        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            width: { xs: "100%", sm: "auto" },
            justifyContent: { xs: "flex-end", sm: "flex-start" },
          }}
        >
          <Button
            variant="outlined"
            size="small"
            startIcon={<CalendarTodayIcon fontSize="small" />}
            endIcon={
              filters.sort_order === "asc" ? (
                <ArrowUpwardIcon fontSize="small" />
              ) : (
                <ArrowDownwardIcon fontSize="small" />
              )
            }
            onClick={toggleDateSort}
            sx={{
              borderRadius: 2,
              textTransform: "none",
              color: "text.primary",
              borderColor: "divider",
              fontWeight: 600,
              px: 2,
            }}
          >
            Date
          </Button>

          <Tooltip title={hasActiveFilters ? "Reset" : "No filters active"}>
            <span>
              <IconButton
                onClick={handleReset}
                disabled={!hasActiveFilters}
                size="small"
                sx={{
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 2,
                  bgcolor: hasActiveFilters ? "action.hover" : "transparent",
                  "&:hover": { bgcolor: "error.lighter", color: "error.main" },
                }}
              >
                <RestartAltIcon fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );
};

export default TransactionFilters;
