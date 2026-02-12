import { useMemo } from "react";
import { ThemeProvider, CssBaseline, useMediaQuery } from "@mui/material";
import { useAuth0 } from "@auth0/auth0-react";
import { useGetUser } from "../features/auth/useGetUser";
import { lightTheme, darkTheme } from "../theme";

/**
 * Dynamic Theme Provider that switches between light/dark mode
 * based on user settings or system preference.
 */
export default function DynamicThemeProvider({ children }) {
  const { isAuthenticated } = useAuth0();
  const { data: user } = useGetUser();
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

  const theme = useMemo(() => {
    // Only use user settings if authenticated
    const themeSetting = isAuthenticated ? (user?.settings?.theme || "system") : "system";

    if (themeSetting === "dark") {
      return darkTheme;
    }
    if (themeSetting === "light") {
      return lightTheme;
    }
    // "system" - use OS preference
    return prefersDarkMode ? darkTheme : lightTheme;
  }, [isAuthenticated, user?.settings?.theme, prefersDarkMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
