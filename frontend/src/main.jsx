import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { lightTheme } from "./theme";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import App from "./App.jsx";
import Auth0ProviderWithNavigate from "./auth/Auth0Provider.jsx";
import DynamicThemeProvider from "./components/DynamicThemeProvider.jsx";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Don't retry on 401/403 errors - these are auth issues, not transient failures
      retry: (failureCount, error) => {
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          return false;
        }
        return failureCount < 3;
      },
      // Prevent aggressive refetching that could cause auth issues
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
    mutations: {
      // Don't retry mutations - they should be explicit
      retry: false,
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider theme={lightTheme}>
          <CssBaseline />
          <Auth0ProviderWithNavigate>
            <DynamicThemeProvider>
              <App />
            </DynamicThemeProvider>
          </Auth0ProviderWithNavigate>
        </ThemeProvider>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
);
