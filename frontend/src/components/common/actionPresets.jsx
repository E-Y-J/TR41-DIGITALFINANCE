/**
 * Action presets for common confirmation patterns in AI chat
 *
 * These presets define button configurations for different types
 * of user confirmations required by the AI assistant.
 */

import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";

// Preset action configurations for common use cases
export const ACTION_PRESETS = {
  // Yes/No confirmation
  CONFIRM: [
    {
      label: "Yes",
      value: "yes",
      variant: "contained",
      color: "primary",
      icon: <CheckIcon fontSize="small" />,
    },
    {
      label: "No",
      value: "no",
      variant: "outlined",
      color: "inherit",
      icon: <CloseIcon fontSize="small" />,
    },
  ],

  // Yes/No/Edit for transaction confirmations
  CONFIRM_WITH_EDIT: [
    {
      label: "Yes, add it",
      value: "yes",
      variant: "contained",
      color: "primary",
      icon: <CheckIcon fontSize="small" />,
    },
    {
      label: "No",
      value: "no",
      variant: "outlined",
      color: "inherit",
      icon: <CloseIcon fontSize="small" />,
    },
    {
      label: "Edit details",
      value: "edit",
      variant: "text",
      color: "primary",
      icon: <EditIcon fontSize="small" />,
    },
  ],

  // Simple OK acknowledgment
  ACKNOWLEDGE: [
    {
      label: "Got it",
      value: "ok",
      variant: "outlined",
      color: "primary",
    },
  ],
};
