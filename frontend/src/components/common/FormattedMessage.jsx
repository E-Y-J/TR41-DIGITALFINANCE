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
} from "@mui/material";

// Render a single line with inline formatting
const FormattedLine = memo(({ text, sx = {} }) => {
  // Parse for bold (**text**), italic (*text*), and code (`text`)
  const segments = useMemo(() => {
    const result = [];
    let remaining = text;
    let key = 0;

    while (remaining.length > 0) {
      // Check for bold
      const boldMatch = remaining.match(/^\*\*(.+?)\*\*/);
      if (boldMatch) {
        result.push(
          <Typography
            key={key++}
            component="span"
            sx={{ fontWeight: 700, ...sx }}
          >
            {boldMatch[1]}
          </Typography>
        );
        remaining = remaining.slice(boldMatch[0].length);
        continue;
      }

      // Check for code
      const codeMatch = remaining.match(/^`(.+?)`/);
      if (codeMatch) {
        result.push(
          <Box
            key={key++}
            component="code"
            sx={{
              bgcolor: "grey.100",
              px: 0.75,
              py: 0.25,
              borderRadius: 0.5,
              fontFamily: "monospace",
              fontSize: "0.85em",
              ...sx,
            }}
          >
            {codeMatch[1]}
          </Box>
        );
        remaining = remaining.slice(codeMatch[0].length);
        continue;
      }

      // Check for italic (single asterisk)
      const italicMatch = remaining.match(/^\*([^*]+?)\*/);
      if (italicMatch) {
        result.push(
          <Typography key={key++} component="span" sx={{ fontStyle: "italic", ...sx }}>
            {italicMatch[1]}
          </Typography>
        );
        remaining = remaining.slice(italicMatch[0].length);
        continue;
      }

      // No pattern matched - find the next special character or take all remaining
      const nextSpecial = remaining.search(/\*|`/);
      if (nextSpecial === -1) {
        // No more special characters
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining}
          </Typography>
        );
        break;
      } else if (nextSpecial > 0) {
        // Text before the next special character
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining.slice(0, nextSpecial)}
          </Typography>
        );
        remaining = remaining.slice(nextSpecial);
      } else {
        // Special character at start but no pattern matched - treat as literal
        result.push(
          <Typography key={key++} component="span" sx={sx}>
            {remaining[0]}
          </Typography>
        );
        remaining = remaining.slice(1);
      }
    }

    return result;
  }, [text, sx]);

  return <>{segments}</>;
});

// Parse table from markdown
const parseTable = (lines) => {
  const rows = lines
    .filter((line) => line.startsWith("|") && !line.match(/^\|[\s-:|]+\|$/))
    .map((line) =>
      line
        .split("|")
        .slice(1, -1)
        .map((cell) => cell.trim())
    );

  if (rows.length < 1) return null;

  const headers = rows[0];
  const bodyRows = rows.slice(1);

  return { headers, bodyRows };
};

const FormattedMessage = memo(({ text, variant = "body2", sx = {} }) => {
  const elements = useMemo(() => {
    if (!text) return null;

    const lines = text.split("\n");
    const result = [];
    let key = 0;
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];
      const trimmedLine = line.trim();

      // Empty line - add spacing
      if (!trimmedLine) {
        result.push(<Box key={key++} sx={{ height: 8 }} />);
        i++;
        continue;
      }

      // Horizontal divider
      if (trimmedLine === "---" || trimmedLine === "***") {
        result.push(
          <Divider key={key++} sx={{ my: 1.5, borderColor: "grey.300" }} />
        );
        i++;
        continue;
      }

      // Table (starts with |)
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
              sx={{ my: 1, border: "1px solid", borderColor: "grey.200" }}
            >
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: "grey.50" }}>
                    {tableData.headers.map((h, idx) => (
                      <TableCell
                        key={idx}
                        sx={{ fontWeight: 600, fontSize: "0.8rem" }}
                      >
                        <FormattedLine text={h} />
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tableData.bodyRows.map((row, rowIdx) => (
                    <TableRow key={rowIdx}>
                      {row.map((cell, cellIdx) => (
                        <TableCell key={cellIdx} sx={{ fontSize: "0.8rem" }}>
                          <FormattedLine text={cell} />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          );
        }
        continue;
      }

      // Bullet list
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
          <List key={key++} dense sx={{ py: 0, pl: 1 }}>
            {listItems.map((item, idx) => (
              <ListItem key={idx} sx={{ py: 0.25, px: 0 }}>
                <Box
                  component="span"
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    bgcolor: "primary.main",
                    mr: 1.5,
                    flexShrink: 0,
                  }}
                />
                <ListItemText
                  primary={<FormattedLine text={item} sx={{ fontSize: "0.875rem" }} />}
                  sx={{ m: 0 }}
                />
              </ListItem>
            ))}
          </List>
        );
        continue;
      }

      // Numbered list
      if (/^\d+\.\s/.test(trimmedLine)) {
        const listItems = [];
        while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
          listItems.push(lines[i].trim().replace(/^\d+\.\s/, ""));
          i++;
        }
        result.push(
          <List key={key++} dense sx={{ py: 0, pl: 1 }}>
            {listItems.map((item, idx) => (
              <ListItem key={idx} sx={{ py: 0.25, px: 0 }}>
                <Typography
                  component="span"
                  sx={{
                    minWidth: 20,
                    fontWeight: 600,
                    color: "primary.main",
                    mr: 1,
                    fontSize: "0.875rem",
                  }}
                >
                  {idx + 1}.
                </Typography>
                <ListItemText
                  primary={<FormattedLine text={item} sx={{ fontSize: "0.875rem" }} />}
                  sx={{ m: 0 }}
                />
              </ListItem>
            ))}
          </List>
        );
        continue;
      }

      // Regular text line
      result.push(
        <Typography
          key={key++}
          variant={variant}
          sx={{
            fontWeight: 500,
            lineHeight: 1.6,
            fontSize: { xs: "0.9rem", sm: "0.875rem" },
            ...sx,
          }}
        >
          <FormattedLine text={line} />
        </Typography>
      );
      i++;
    }

    return result;
  }, [text, variant, sx]);

  return (
    <Box
      sx={{
        "& > *:first-of-type": { mt: 0 },
        "& > *:last-child": { mb: 0 },
      }}
    >
      {elements}
    </Box>
  );
});

FormattedMessage.displayName = "FormattedMessage";
FormattedLine.displayName = "FormattedLine";

export default FormattedMessage;
