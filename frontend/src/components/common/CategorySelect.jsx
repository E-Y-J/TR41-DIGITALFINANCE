import { TextField, MenuItem, InputAdornment } from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import { CATEGORIES } from "../../utils/constants";

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

const CategorySelect = ({ value, onChange, sx = {} }) => {
  return (
    <TextField
      select
      label="Category"
      size="small"
      value={value || "All"}
      onChange={(e) => onChange(e.target.value)}
      sx={{
        ...textFieldStyles,
        minWidth: 180,
        ...sx,
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
                "& .MuiList-root": { p: 1 },
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
  );
};

export default CategorySelect;
