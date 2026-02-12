import { useMemo, useCallback } from "react";
import { useGetUser } from "../features/auth/useGetUser";

/**
 * Hook for formatting currency and dates based on user preferences.
 * Uses user's settings for currency and timezone from the backend.
 */
export function useFormatting() {
  const { data: user } = useGetUser();

  // Get user preferences with defaults
  const currency = user?.settings?.currency || "USD";
  const timezone = user?.settings?.timezone || "UTC";

  // Currency formatter
  const currencyFormatter = useMemo(() => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }, [currency]);

  // Format a number as currency
  const formatCurrency = useCallback(
    (amount) => {
      if (amount === null || amount === undefined) return "-";
      return currencyFormatter.format(amount);
    },
    [currencyFormatter]
  );

  // Format a date with user's timezone
  const formatDate = useCallback(
    (date, options = {}) => {
      if (!date) return "-";
      const dateObj = typeof date === "string" ? new Date(date) : date;
      
      const defaultOptions = {
        timeZone: timezone,
        year: "numeric",
        month: "short",
        day: "numeric",
        ...options,
      };

      return new Intl.DateTimeFormat("en-US", defaultOptions).format(dateObj);
    },
    [timezone]
  );

  // Format date with time
  const formatDateTime = useCallback(
    (date, options = {}) => {
      if (!date) return "-";
      const dateObj = typeof date === "string" ? new Date(date) : date;

      const defaultOptions = {
        timeZone: timezone,
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        ...options,
      };

      return new Intl.DateTimeFormat("en-US", defaultOptions).format(dateObj);
    },
    [timezone]
  );

  // Format relative time (e.g., "2 days ago")
  const formatRelativeTime = useCallback(
    (date) => {
      if (!date) return "-";
      const dateObj = typeof date === "string" ? new Date(date) : date;
      const now = new Date();
      const diffInSeconds = Math.floor((now - dateObj) / 1000);

      const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

      if (diffInSeconds < 60) {
        return rtf.format(-diffInSeconds, "second");
      } else if (diffInSeconds < 3600) {
        return rtf.format(-Math.floor(diffInSeconds / 60), "minute");
      } else if (diffInSeconds < 86400) {
        return rtf.format(-Math.floor(diffInSeconds / 3600), "hour");
      } else if (diffInSeconds < 2592000) {
        return rtf.format(-Math.floor(diffInSeconds / 86400), "day");
      } else if (diffInSeconds < 31536000) {
        return rtf.format(-Math.floor(diffInSeconds / 2592000), "month");
      } else {
        return rtf.format(-Math.floor(diffInSeconds / 31536000), "year");
      }
    },
    []
  );

  // Get currency symbol only
  const getCurrencySymbol = useCallback(() => {
    return currencyFormatter.formatToParts(0).find((part) => part.type === "currency")?.value || "$";
  }, [currencyFormatter]);

  return {
    currency,
    timezone,
    formatCurrency,
    formatDate,
    formatDateTime,
    formatRelativeTime,
    getCurrencySymbol,
  };
}
