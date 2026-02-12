/**
 * ActionButtons - Reusable quick action buttons for AI chat confirmations
 *
 * Usage:
 *   <ActionButtons
 *     actions={[
 *       { label: "Yes", value: "yes", variant: "contained", color: "primary" },
 *       { label: "No", value: "no", variant: "outlined", color: "secondary" },
 *     ]}
 *     onAction={(value) => handleUserResponse(value)}
 *   />
 *
 * Props:
 *   actions - Array of action objects with label, value, variant, color
 *   onAction - Callback when a button is clicked, receives the action value
 *   disabled - Disable all buttons (e.g., while processing)
 *   size - Button size: "small" | "medium" | "large"
 *   fullWidth - Make buttons take full width
 *   direction - "row" | "column" layout direction
 */

import { memo } from "react";
import { Box, Button, Stack, Fade } from "@mui/material";
import { ACTION_PRESETS } from "./actionPresets";

// Re-export for convenience
export { ACTION_PRESETS } from "./actionPresets";

const ActionButtons = memo(
  ({
    actions = ACTION_PRESETS.CONFIRM,
    onAction,
    disabled = false,
    size = "small",
    fullWidth = false,
    direction = "row",
    show = true,
  }) => {
    if (!show || !actions || actions.length === 0) {
      return null;
    }

    return (
      <Fade in={show} timeout={300}>
        <Box sx={{ mt: 1.5, mb: 0.5 }}>
          <Stack
            direction={direction}
            spacing={1}
            sx={{
              flexWrap: "wrap",
              gap: 1,
            }}
          >
            {actions.map((action) => (
              <Button
                key={action.value}
                variant={action.variant || "outlined"}
                color={action.color || "primary"}
                size={size}
                disabled={disabled}
                fullWidth={fullWidth}
                startIcon={action.icon}
                onClick={() => onAction?.(action.value)}
                sx={{
                  borderRadius: 2,
                  textTransform: "none",
                  fontWeight: 500,
                  minWidth: action.icon ? 100 : 80,
                  px: 2,
                  py: 0.75,
                  boxShadow: action.variant === "contained" ? 1 : 0,
                  "&:hover": {
                    boxShadow:
                      action.variant === "contained"
                        ? 2
                        : "0 0 0 1px currentColor",
                  },
                }}
              >
                {action.label}
              </Button>
            ))}
          </Stack>
        </Box>
      </Fade>
    );
  }
);

ActionButtons.displayName = "ActionButtons";

export default ActionButtons;
