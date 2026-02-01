import {
  TextField,
  MenuItem,
  InputAdornment,
  IconButton,
  Tooltip,
  Box,
  Button,
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import FilterListIcon from "@mui/icons-material/FilterList";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import MoneyOffIcon from "@mui/icons-material/MoneyOff";
import AppsIcon from "@mui/icons-material/Apps";

const CATEGORIES = [
  "Food & Dining",
  "Transportation",
  "Shopping & Retail",
  "Entertainment & Recreation",
  "Healthcare & Medical",
  "Utilities & Services",
  "Financial Services",
  "Income",
  "Government & Legal",
  "Charity & Donations",
];

const getButtonStyle = (isActive) => ({
  textTransform: "none",
  fontWeight: 600,
  borderRadius: 2,
  px: 2,
  minWidth: "fit-content",
  color: isActive ? "common.white" : "text.secondary",
  bgcolor: isActive ? "primary.main" : "transparent",
  border: "1px solid",
  borderColor: isActive ? "primary.main" : "divider",
  "&:hover": {
    bgcolor: isActive ? "primary.dark" : "action.hover",
    borderColor: isActive ? "primary.dark" : "grey.400",
  },
});

const styledMenuItem = {
  borderRadius: 2,
  mx: 1,
  my: 0.5,
  typography: "body2",
  transition: "all 0.2s",

  "&:hover": {
    bgcolor: "grey.100",
    transform: "translateY(-1px)",
  },

  "&.Mui-selected": {
    bgcolor: "primary.main",
    color: "white",
    fontWeight: 600,
  },
  "&.Mui-selected:hover": {
    bgcolor: "primary.light",
  },
};

const textFieldStyles = {
  flex: 1,
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
};

const TransactionFilters = ({ filters, onFilterChange }) => {
  const handleChange = (field, value) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const handleReset = () => {
    onFilterChange({ search: "", category: "All", type: "All" });
  };

  const hasActiveFilters =
    filters.search?.trim() !== "" ||
    (filters.category !== "All" && filters.category !== "") ||
    (filters.type !== "All" && filters.type !== "");

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 2,
        flexWrap: "wrap",
        width: "100%",
      }}
    >
      <Box
        sx={{
          display: "flex",
          gap: 2,
          flex: "1 1 400px",
          minWidth: { xs: "100%", md: "400px" },
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

        <TextField
          select
          label="Category"
          size="small"
          value={filters.category || "All"}
          onChange={(e) => handleChange("category", e.target.value)}
          sx={{
            ...textFieldStyles,
            minWidth: { xs: 140, sm: 180 },
            flex: "0 1 auto",
          }}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <FilterListIcon fontSize="small" color="action" />
                </InputAdornment>
              ),
            },
            select: {
              MenuProps: {
                PaperProps: {
                  elevation: 3,
                  sx: {
                    maxHeight: 300,
                    borderRadius: 3,
                    mt: 1,
                    bgcolor: "background.paper",
                    boxShadow: "0px 4px 20px rgba(0,0,0,0.1)",
                    "& .MuiList-root": {
                      p: 1,
                    },
                  },
                },
                disableScrollLock: true,
              },
            },
          }}
        >
          <MenuItem value="All" sx={styledMenuItem}>
            All Categories
          </MenuItem>
          {CATEGORIES.map((cat) => (
            <MenuItem key={cat} value={cat} sx={styledMenuItem}>
              {cat}
            </MenuItem>
          ))}
        </TextField>
      </Box>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          ml: { xs: 0, lg: "auto" },
          width: { xs: "100%", sm: "auto" },
          justifyContent: { xs: "space-between", sm: "flex-start" },
          pl: { xs: 0, lg: 2 },
          borderLeft: { xs: "none", lg: "1px solid" },
          borderColor: { lg: "divider" },
          height: { lg: 32 },
        }}
      >
        <Box sx={{ display: "flex", gap: 1, flexWrap: "nowrap" }}>
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

        <Tooltip
          title={hasActiveFilters ? "Reset Filters" : "No filters active"}
        >
          <span>
            <IconButton
              onClick={handleReset}
              disabled={!hasActiveFilters}
              size="small"
              sx={{
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 2,
                p: 1,
                "&.Mui-disabled": { borderColor: "grey.100" },
              }}
            >
              <RestartAltIcon fontSize="small" />
            </IconButton>
          </span>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default TransactionFilters;
