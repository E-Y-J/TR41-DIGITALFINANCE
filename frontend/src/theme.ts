import { createTheme, ThemeOptions } from "@mui/material/styles";

declare module "@mui/material/styles" {
  interface Palette {
    tertiary: Palette["primary"];
    neutral: Palette["primary"];
  }
  interface PaletteOptions {
    tertiary?: PaletteOptions["primary"];
    neutral?: PaletteOptions["primary"];
  }
}

// =============================================================================
// Shared component styles for consistent theming
// =============================================================================
const sharedComponents: ThemeOptions["components"] = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        textTransform: "none",
        fontWeight: 600,
      },
    },
  },
  MuiTextField: {
    defaultProps: {
      variant: "outlined",
    },
  },
  MuiOutlinedInput: {
    styleOverrides: {
      root: {
        borderRadius: 10,
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: "none",
        borderRadius: 12,
      },
    },
  },
};

const typography = {
  fontFamily: "'Inter', sans-serif",
  h1: { fontWeight: 700 },
  h6: { fontWeight: 600, fontSize: "1.1rem" },
  button: { fontWeight: 600 },
  allVariants: {
    fontFeatureSettings: "'cv11', 'ss01'",
  },
};

export const lightTheme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#1E88E5", light: "#60A5FA" },
    secondary: { main: "#2ECC71", light: "#6EE7B7" },
    neutral: { main: "#475569" },
    background: {
      default: "#F8FAFC",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#0F172A",
      secondary: "#64748B",
    },

    action: {
      hover: "#F8FAFC",
      selected: "#F1F5F9",
      focus: "#E2E8F0",
    },
  },
  typography,
  components: sharedComponents,
});

export const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#60A5FA", light: "#93C5FD" },
    secondary: { main: "#6EE7B7", light: "#A7F3D0" },
    neutral: { main: "#94A3B8" },
    background: {
      default: "#0F172A",
      paper: "#1E293B",
    },
    text: {
      primary: "#F8FAFC",
      secondary: "#94A3B8",
    },

    action: {
      hover: "#1E293B",
      selected: "#334155",
      focus: "#475569",
    },
  },
  typography,
  components: sharedComponents,
});

export const theme = lightTheme;
