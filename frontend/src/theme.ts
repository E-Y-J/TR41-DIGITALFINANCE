import { createTheme } from "@mui/material/styles";

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

// Shared typography settings
const typography = {
  fontFamily: "'Inter', sans-serif",
  h1: { fontWeight: 700 },
  h2: { fontWeight: 700 },
  h3: { fontWeight: 600 },
  allVariants: {
    fontFeatureSettings: "'cv11', 'ss01'",
  },
  body1: {
    fontFeatureSettings: "'tnum'",
  },
  body2: {
    fontFeatureSettings: "'tnum'",
  },
};

// Light theme
export const lightTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1E88E5",
      light: "#60A5FA",
    },
    secondary: {
      main: "#2ECC71",
      light: "#6EE7B7",
    },
    neutral: {
      main: "#2C2F33",
    },
    background: {
      default: "#F1F5F9",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#020617",
      secondary: "#2C2F33",
    },
  },
  typography,
});

// Dark theme
export const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#60A5FA",
      light: "#93C5FD",
    },
    secondary: {
      main: "#6EE7B7",
      light: "#A7F3D0",
    },
    neutral: {
      main: "#9CA3AF",
    },
    background: {
      default: "#0F172A",
      paper: "#1E293B",
    },
    text: {
      primary: "#F1F5F9",
      secondary: "#CBD5E1",
    },
  },
  typography,
});

// Default export for backward compatibility
export const theme = lightTheme;
