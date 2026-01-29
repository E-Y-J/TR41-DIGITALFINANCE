import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  alpha,
  useTheme,
  Chip,
} from "@mui/material";

import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import VolunteerActivismIcon from "@mui/icons-material/VolunteerActivism";
import TheaterComedyIcon from "@mui/icons-material/TheaterComedy";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import FastfoodIcon from "@mui/icons-material/Fastfood";
import GavelIcon from "@mui/icons-material/Gavel";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import ShoppingBagIcon from "@mui/icons-material/ShoppingBag";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
};

const getIcon = (categoryName = "") => {
  const lowerName = categoryName.toLowerCase();
  if (lowerName.includes("charity"))
    return <VolunteerActivismIcon fontSize="small" />;
  if (lowerName.includes("entertainment"))
    return <TheaterComedyIcon fontSize="small" />;
  if (lowerName.includes("financial"))
    return <AccountBalanceIcon fontSize="small" />;
  if (lowerName.includes("food")) return <FastfoodIcon fontSize="small" />;
  if (lowerName.includes("government")) return <GavelIcon fontSize="small" />;
  if (lowerName.includes("health"))
    return <MedicalServicesIcon fontSize="small" />;
  if (lowerName.includes("income")) return <AttachMoneyIcon fontSize="small" />;
  if (lowerName.includes("shopping"))
    return <ShoppingBagIcon fontSize="small" />;
  if (lowerName.includes("transportation"))
    return <DirectionsCarIcon fontSize="small" />;
  if (lowerName.includes("utilit")) return <LightbulbIcon fontSize="small" />;
  return <LocalOfferIcon fontSize="small" />;
};

const TransactionTable = ({ data = [], isDashboard = false }) => {
  const theme = useTheme();
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

  const getStatusChip = (status = "completed") => {
    const s = status.toLowerCase();
    let label = status;

    if (s === "completed" || s === "posted") {
      label = "Posted";
    } else if (s === "pending") {
      label = "Pending";
    } else if (s === "failed") {
      label = "Failed";
    }

    return (
      <Chip
        label={label}
        size="small"
        variant="outlined"
        sx={{
          height: 24,
          fontSize: "0.75rem",
          fontWeight: 600,
          border: "1px solid",
          borderColor:
            s === "pending"
              ? "warning.light"
              : s === "completed"
                ? "success.light"
                : "error.light",
          bgcolor:
            s === "pending"
              ? alpha(theme.palette.warning.main, 0.05)
              : s === "completed"
                ? alpha(theme.palette.success.main, 0.05)
                : alpha(theme.palette.error.main, 0.05),
          color:
            s === "pending"
              ? "warning.dark"
              : s === "completed"
                ? "success.dark"
                : "error.dark",
          "& .MuiChip-icon": { color: "inherit" },
        }}
      />
    );
  };

  return (
    <TableContainer sx={{ width: "100%", overflowX: "auto" }}>
      <Table
        aria-label="transaction table"
        sx={{
          tableLayout: "fixed",
          minWidth: { xs: "100%", sm: 400 },
        }}
      >
        <TableHead>
          <TableRow>
            <TableCell
              sx={{
                ...headerStyle,
                width: "120px",
                pl: 0,
                display: { xs: "none", sm: "table-cell" },
              }}
            >
              Date
            </TableCell>

            <TableCell
              sx={{
                ...headerStyle,
                pl: { xs: 0, sm: 2 },
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
                width: { xs: "90px", sm: "120px" },
                minWidth: { xs: "90px", sm: "120px" },
              }}
            >
              Amount
            </TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {data && data.length > 0 ? (
            data.map((row, index) => {
              const currentFormattedDate = formatDate(row.date);
              const prevFormattedDate =
                index > 0 ? formatDate(data[index - 1].date) : null;
              const showDate =
                index === 0 || currentFormattedDate !== prevFormattedDate;
              const isIncome = row.transaction_type === "income";
              const amountColor = isIncome ? "success.main" : "text.primary";
              const amountPrefix = isIncome ? "+" : "";
              const formattedAmount = `${amountPrefix}$${parseFloat(row.amount).toFixed(2)}`;

              const rowStatus =
                row.status || (index === 0 ? "pending" : "completed");

              return (
                <TableRow
                  key={row.id}
                  hover
                  onClick={(event) => handleRowClick(event, row)}
                  sx={{
                    cursor: "pointer",
                    "& td": {
                      py: 2,
                      borderBottom: "1px solid",
                      borderColor: "divider",
                    },
                    "&:last-child td": { borderBottom: 0 },
                    transition: "all 0.2s",
                    "&:hover": {
                      bgcolor: alpha(theme.palette.primary.main, 0.04),
                    },
                  }}
                >
                  <TableCell
                    sx={{
                      pl: 0,
                      verticalAlign: "top",
                      display: { xs: "none", sm: "table-cell" },
                    }}
                  >
                    {showDate && (
                      <Typography
                        variant="caption"
                        fontWeight={700}
                        color="text.secondary"
                        sx={{
                          display: "block",
                          mt: 0.5,
                          textTransform: "uppercase",
                          fontSize: "0.75rem",
                          letterSpacing: "0.5px",
                        }}
                      >
                        {currentFormattedDate}
                      </Typography>
                    )}
                  </TableCell>

                  <TableCell
                    component="th"
                    scope="row"
                    sx={{
                      verticalAlign: "top",
                      pl: { xs: 0, sm: 2 },
                      width: "auto",
                      maxWidth: 0,
                      overflow: "hidden",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        minWidth: 0,
                      }}
                    >
                      <Box sx={{ display: { xs: "block", sm: "none" }, mb: 1 }}>
                        {showDate && (
                          <Typography
                            variant="caption"
                            fontWeight={700}
                            color="text.secondary"
                            sx={{
                              textTransform: "uppercase",
                              letterSpacing: "0.5px",
                            }}
                          >
                            {currentFormattedDate}
                          </Typography>
                        )}
                      </Box>

                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          minWidth: 0,
                        }}
                      >
                        <Avatar
                          variant="rounded"
                          sx={{
                            bgcolor: "grey.100",
                            color: "primary.main",
                            width: 32,
                            height: 32,
                            borderRadius: 3,
                            flexShrink: 0,
                          }}
                        >
                          {getIcon(row.category_name)}
                        </Avatar>
                        <Box sx={{ minWidth: 0, flex: 1, overflow: "hidden" }}>
                          <Typography
                            variant="body2"
                            fontWeight={600}
                            color="text.primary"
                            noWrap
                            sx={{
                              fontSize: { xs: "0.8rem", sm: "0.875rem" },
                              display: "block",
                            }}
                          >
                            {row.merchant_name || "Unknown Merchant"}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </TableCell>

                  {isDashboard ? null : (
                    <TableCell
                      sx={{
                        verticalAlign: "middle",
                        display: { xs: "none", md: "table-cell" },
                      }}
                    >
                      {getStatusChip(rowStatus)}
                    </TableCell>
                  )}

                  <TableCell
                    align="right"
                    sx={{
                      verticalAlign: "top",
                      pr: 0,
                      width: { xs: "90px", sm: "120px" },
                      minWidth: { xs: "90px", sm: "120px" },
                    }}
                  >
                    <Typography
                      variant="body2"
                      fontWeight={700}
                      noWrap
                      sx={{
                        fontSize: { xs: "0.8rem", sm: "0.875rem" },
                        mt: { xs: showDate ? 3.2 : 0.5, sm: 0.5 },
                        color: amountColor,
                      }}
                    >
                      {formattedAmount}
                    </Typography>
                  </TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell
                colSpan={5}
                align="center"
                sx={{
                  py: 8,
                  color: "text.secondary",
                  fontSize: "1rem",
                  borderBottom: "none",
                }}
              >
                No transactions available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <Menu
        open={contextMenu !== null}
        onClose={handleMenuClose}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
        slotProps={{
          paper: {
            elevation: 3,
            sx: {
              borderRadius: 2,
              minWidth: 180,
              overflow: "visible",
              filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
              mt: 0,
            },
          },
        }}
      >
        <Box
          sx={{
            px: 2,
            py: 1.5,
            borderBottom: "1px solid",
            borderColor: "divider",
            bgcolor: "grey.50",
            outline: "none",
          }}
        >
          <Typography
            variant="caption"
            display="block"
            color="text.secondary"
            fontWeight={700}
            sx={{ fontSize: "0.7rem" }}
          >
            MANAGE
          </Typography>
          <Typography
            variant="body2"
            fontWeight={600}
            noWrap
            sx={{ maxWidth: 200 }}
          >
            {selectedRow?.merchant_name || "Transaction"}
          </Typography>
        </Box>

        <MenuItem onClick={handleMenuClose} dense sx={{ py: 1, mt: 0.5 }}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit
        </MenuItem>

        <MenuItem
          onClick={handleMenuClose}
          dense
          sx={{ color: "error.main", py: 1 }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          Delete
        </MenuItem>
      </Menu>
    </TableContainer>
  );
};

export default TransactionTable;
