import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import EmptyState from "../../../components/common/EmptyState";
import TransactionActionMenu from "./TransactionActionMenu";

import { TransactionRow } from "./TransactionRow";
import { formatDate } from "../../../utils/constants";

const headerStyle = {
  color: "text.secondary",
  fontSize: "0.75rem",
  fontWeight: 700,
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  borderBottom: "1px solid",
  borderColor: "divider",
  pb: 1.5,
  whiteSpace: "nowrap",
};

const TransactionTable = ({ data = [], isDashboard = false }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedRow, setSelectedRow] = useState(null);

  const handleMenuClose = () => {
    setContextMenu(null);
  };

  const handleRowClick = (event, row) => {
    event.preventDefault();
    setSelectedRow(row);
    setContextMenu(
      contextMenu === null
        ? {
            mouseX: event.clientX + 2,
            mouseY: event.clientY - 6,
          }
        : null,
    );
  };

  const handleEdit = (row) => {
    console.log("Editing", row);
  };

  const handleDelete = (row) => {
    console.log("Deleting", row);
  };

  if (!data || data.length === 0)
    return (
      <EmptyState
        header="No transactions found"
        text="We couldn't find any transactions matching your filters. Try adjusting your search or category."
      />
    );

  return (
    <TableContainer sx={{ width: "100%", overflowX: "auto" }}>
      <Table
        aria-label="transaction table"
        sx={{
          width: "100%",
          minWidth: { xs: "100%", sm: 400 },
        }}
      >
        <TableHead>
          <TableRow>
            <TableCell
              sx={{
                ...headerStyle,
                width: "140px",
                pl: 3,
                display: { xs: "none", sm: "table-cell" },
              }}
            >
              Date
            </TableCell>

            <TableCell
              sx={{
                ...headerStyle,
                pl: { xs: 2, sm: 2 },
                width: "auto",
              }}
            >
              Merchant
            </TableCell>

            {isDashboard ? null : (
              <TableCell
                sx={{
                  ...headerStyle,
                  width: "100px",
                  minWidth: "100px",
                  display: { xs: "none", md: "table-cell" },
                }}
              >
                Status
              </TableCell>
            )}

            <TableCell
              align="right"
              sx={{
                ...headerStyle,
                pr: { xs: 2, sm: 3 },
                width: { xs: "90px", sm: "120px" },
                minWidth: { xs: "90px", sm: "120px" },
              }}
            >
              Amount
            </TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {data.map((row, index) => {
            const currentFormattedDate = formatDate(row.date);
            const prevFormattedDate =
              index > 0 ? formatDate(data[index - 1].date) : null;
            const showDate =
              index === 0 || currentFormattedDate !== prevFormattedDate;

            return (
              <TransactionRow
                key={row.id}
                row={row}
                showDate={showDate}
                formattedDate={currentFormattedDate}
                onClick={handleRowClick}
                isDashboard={isDashboard}
              />
            );
          })}
        </TableBody>
      </Table>
      <TransactionActionMenu
        contextMenu={contextMenu}
        onClose={handleMenuClose}
        selectedRow={selectedRow}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </TableContainer>
  );
};

export default TransactionTable;
