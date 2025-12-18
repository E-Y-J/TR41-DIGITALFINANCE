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

export const theme = createTheme({
  palette: {
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

  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});
