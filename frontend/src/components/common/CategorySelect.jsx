import { TextField, MenuItem, InputAdornment, useTheme } from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import { CATEGORIES } from "../../utils/constants";

const styledMenuItem = (theme) => ({
  borderRadius: 2,
  mx: 1,
  my: 0.5,
  typography: "body2",
  transition: "all 0.2s",

  "&:hover": {
    bgcolor: theme.palette.mode === "light" ? "grey.100" : "action.hover",
    transform: "translateY(-1px)",
  },
  "&.Mui-selected": {
    bgcolor: "primary.main",
    color: "primary.contrastText",
    fontWeight: 600,
  },
  "&.Mui-selected:hover": {
    bgcolor: "primary.light",
  },
});

const textFieldStyles = (theme) => ({
  "& .MuiOutlinedInput-root": {
    borderRadius: 3,

    backgroundColor:
      theme.palette.mode === "light" ? "grey.50" : "background.paper",
    transition: "all 0.2s ease-in-out",
    "&:hover": {
      backgroundColor:
        theme.palette.mode === "light" ? "grey.100" : "action.hover",
      "& .MuiOutlinedInput-notchedOutline": {
        borderColor:
          theme.palette.mode === "light" ? "grey.400" : "primary.main",
      },
    },
    "&.Mui-focused": {
      backgroundColor: "background.paper",
      boxShadow:
        theme.palette.mode === "light"
          ? "0 4px 12px rgba(0,0,0,0.05)"
          : "0 4px 12px rgba(0,0,0,0.5)",
    },
  },
});

const CategorySelect = ({ value, onChange, sx = {} }) => {
  const theme = useTheme();

  return (
    <TextField
      select
      label="Category"
      size="small"
      value={value || "All"}
      onChange={(e) => onChange(e.target.value)}
      sx={{
        ...textFieldStyles(theme),
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
              elevation: 4,
              sx: {
                maxHeight: 300,
                borderRadius: 3,
                mt: 1,
                bgcolor: "background.paper",
                backgroundImage: "none",
                border:
                  theme.palette.mode === "dark"
                    ? `1px solid ${theme.palette.divider}`
                    : "none",
                "& .MuiList-root": { p: 1 },
              },
            },
            disableScrollLock: true,
          },
        },
      }}
    >
      <MenuItem value="All" sx={styledMenuItem(theme)}>
        All Categories
      </MenuItem>
      {CATEGORIES.map((cat) => (
        <MenuItem key={cat} value={cat} sx={styledMenuItem(theme)}>
          {cat}
        </MenuItem>
      ))}
    </TextField>
  );
};

export default CategorySelect;
