/**
 * FormattedMessage - Rich text formatting for AI chat messages
 *
 * Parses markdown-like patterns in AI responses and renders them
 * with proper styling using MUI components.
 *
 * Supported patterns:
 *   **bold text**     → Bold text
 *   *italic text*     → Italic text
 *   `code`            → Inline code
 *   - item            → Bullet list
 *   1. item           → Numbered list
 *   | table | row |   → Simple table
 *   ---               → Horizontal divider
 *
 * Usage:
 *   <FormattedMessage text="**Summary:** Your spending is $500" />
 */

import { memo, useMemo } from "react";
import {
  Box,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemText,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  alpha,
  useTheme,
} from "@mui/material";

const FormattedLine = memo(({ text, sx = {} }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  const segments = useMemo(() => {
    const result = [];
    let remaining = text;
    let key = 0;

    while (remaining.length > 0) {
      const boldMatch = remaining.match(/^\*\*(.+?)\*\*/);
      if (boldMatch) {
        result.push(
          <Typography
            key={key++}
            component="span"
            sx={{ fontWeight: 700, ...sx }}
          >
            {boldMatch[1]}
          </Typography>,
        );
        remaining = remaining.slice(boldMatch[0].length);
        continue;
      }

      const codeMatch = remaining.match(/^`(.+?)`/);
      if (codeMatch) {
        result.push(
          <Box
            key={key++}
            component="code"
            sx={{
              bgcolor: isDarkMode
                ? alpha(theme.palette.primary.main, 0.15)
                : "grey.100",
              color: isDarkMode ? "primary.light" : "primary.dark",
              px: 0.75,
              py: 0.25,
              borderRadius: 1,
              fontFamily: "'JetBrains Mono', 'Courier New', monospace",
              fontSize: "0.9em",
              border: isDarkMode
                ? `1px solid ${alpha(theme.palette.primary.main, 0.2)}`
                : "1px solid",
              borderColor: isDarkMode ? undefined : "grey.200",
              ...sx,
            }}
          >
            {codeMatch[1]}
          </Box>,
        );
        remaining = remaining.slice(codeMatch[0].length);
        continue;
      }

      const italicMatch = remaining.match(/^\*([^*]+?)\*/);
      if (italicMatch) {
        result.push(
          <Typography
            key={key++}
            component="span"
            sx={{ fontStyle: "italic", ...sx }}
          >
            {italicMatch[1]}
          </Typography>,
        );
        remaining = remaining.slice(italicMatch[0].length);
        continue;
      }

      const nextSpecial = remaining.search(/\*|`/);
      if (nextSpecial === -1) {
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining}
          </Typography>,
        );
        break;
      } else if (nextSpecial > 0) {
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining.slice(0, nextSpecial)}
          </Typography>,
        );
        remaining = remaining.slice(nextSpecial);
      } else {
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining[0]}
          </Typography>,
        );
        remaining = remaining.slice(1);
      }
    }
    return result;
  }, [text, sx, isDarkMode, theme.palette.primary.main]);

  return <>{segments}</>;
});

const parseTable = (lines) => {
  const rows = lines
    .filter((line) => line.startsWith("|") && !line.match(/^\|[\s-:|]+\|$/))
    .map((line) =>
      line
        .split("|")
        .slice(1, -1)
        .map((cell) => cell.trim()),
    );
  if (rows.length < 1) return null;
  return { headers: rows[0], bodyRows: rows.slice(1) };
};

const FormattedMessage = memo(({ text, variant = "body2", sx = {} }) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark";

  const elements = useMemo(() => {
    if (!text) return null;
    const lines = text.split("\n");
    const result = [];
    let key = 0;
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];
      const trimmedLine = line.trim();

      if (!trimmedLine) {
        result.push(<Box key={key++} sx={{ height: 12 }} />);
        i++;
        continue;
      }

      if (trimmedLine === "---" || trimmedLine === "***") {
        result.push(
          <Divider key={key++} sx={{ my: 2.5, borderColor: "divider" }} />,
        );
        i++;
        continue;
      }

      if (trimmedLine.startsWith("|")) {
        const tableLines = [];
        while (i < lines.length && lines[i].trim().startsWith("|")) {
          tableLines.push(lines[i].trim());
          i++;
        }
        const tableData = parseTable(tableLines);
        if (tableData) {
          result.push(
            <TableContainer
              key={key++}
              component={Paper}
              elevation={0}
              sx={{
                my: 2,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper",
                backgroundImage: "none",
                borderRadius: 2,
                overflow: "hidden",
              }}
            >
              <Table size="small">
                <TableHead>
                  <TableRow
                    sx={{
                      bgcolor: isDarkMode
                        ? alpha(theme.palette.primary.main, 0.08)
                        : "grey.50",
                    }}
                  >
                    {tableData.headers.map((h, idx) => (
                      <TableCell
                        key={idx}
                        sx={{
                          fontWeight: 700,
                          py: 1.5,
                          borderColor: "divider",
                        }}
                      >
                        <FormattedLine text={h} />
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tableData.bodyRows.map((row, rowIdx) => (
                    <TableRow
                      key={rowIdx}
                      sx={{
                        "&:last-child td": { border: 0 },
                        "&:hover": { bgcolor: "action.hover" },
                      }}
                    >
                      {row.map((cell, cellIdx) => (
                        <TableCell
                          key={cellIdx}
                          sx={{ borderColor: "divider" }}
                        >
                          <FormattedLine text={cell} />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>,
          );
        }
        continue;
      }

      if (trimmedLine.startsWith("- ") || trimmedLine.startsWith("• ")) {
        const listItems = [];
        while (
          i < lines.length &&
          (lines[i].trim().startsWith("- ") || lines[i].trim().startsWith("• "))
        ) {
          listItems.push(lines[i].trim().slice(2));
          i++;
        }
        result.push(
          <List key={key++} dense sx={{ py: 0.5 }}>
            {listItems.map((item, idx) => (
              <ListItem
                key={idx}
                sx={{ py: 0.5, px: 0, alignItems: "flex-start" }}
              >
                <Box
                  component="span"
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    bgcolor: "primary.main",
                    mt: 1.2,
                    mr: 2,
                    flexShrink: 0,
                  }}
                />
                <ListItemText
                  primary={<FormattedLine text={item} />}
                  sx={{ m: 0 }}
                />
              </ListItem>
            ))}
          </List>,
        );
        continue;
      }

      result.push(
        <Typography
          key={key++}
          variant={variant}
          sx={{
            fontWeight: 500,
            lineHeight: 1.75,
            mb: 1,
            color: isDarkMode ? "text.primary" : "inherit",
            ...sx,
          }}
        >
          <FormattedLine text={line} />
        </Typography>,
      );
      i++;
    }
    return result;
  }, [text, variant, sx, isDarkMode, theme]);
  return (
    <Box
      sx={{ "& > *:first-of-type": { mt: 0 }, "& > *:last-child": { mb: 0 } }}
    >
      {elements}
    </Box>
  );
});

FormattedMessage.displayName = "FormattedMessage";
FormattedLine.displayName = "FormattedLine";

export default FormattedMessage;
