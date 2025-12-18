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

// 2. Define the theme
export const theme = createTheme({
  palette: {
    // BLUE: Your main action color
    primary: {
      main: "#1E88E5",
      light: "#60A5FA",
    },
    // GREEN: Your success/secondary actions
    secondary: {
      main: "#2ECC71",
      light: "#6EE7B7",
    },
    // DARK GRAY: Used for dark accents or neutral elements
    neutral: {
      main: "#2C2F33",
    },
    // BACKGROUNDS
    background: {
      default: "#F1F5F9",
      paper: "#FFFFFF",
    },
    // TEXT
    text: {
      primary: "#020617",
      secondary: "#2C2F33",
    },
  },
  // Optional: Global component overrides
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});
