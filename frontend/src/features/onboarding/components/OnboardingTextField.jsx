import { TextField, InputAdornment } from "@mui/material";

const OnboardingTextField = ({
  label,
  name,
  value,
  error,
  onChange,
  styles,
  type = "text",
  helperText,
  startAdornment,
}) => {
  return (
    <TextField
      label={label}
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      error={error}
      helperText={error ? "Required" : helperText}
      required
      fullWidth
      variant="outlined"
      sx={styles}
      onKeyDown={
        type === "number"
          ? (e) => ["e", "E", "+", "-"].includes(e.key) && e.preventDefault()
          : undefined
      }
      slotProps={{
        input: {
          startAdornment: startAdornment ? (
            <InputAdornment position="start">{startAdornment}</InputAdornment>
          ) : undefined,
        },
      }}
    />
  );
};

export default OnboardingTextField;
