import React, { useState } from "react";
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
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
} from "@mui/material";

// mock values for testing
import ShoppingBagIcon from "@mui/icons-material/ShoppingBag";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import FastfoodIcon from "@mui/icons-material/Fastfood";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import SubscriptionsIcon from "@mui/icons-material/Subscriptions";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

const rows = [
  {
    id: 1,
    name: "Netflix Subscription",
    date: "Jan 12, 2026",
    amount: "$14.99",
  },
  { id: 2, name: "Apple Store", date: "Jan 12, 2026", amount: "$999.00" },
  { id: 3, name: "Pizza Hut", date: "Jan 08, 2026", amount: "$35.50" },
  { id: 4, name: "Uber Ride", date: "Jan 08, 2026", amount: "$12.20" },
  { id: 5, name: "Salary Deposit", date: "Jan 01, 2026", amount: "+$4,500.00" },
];

const getIcon = (name) => {
  if (name.includes("Netflix") || name.includes("Subscription"))
    return <SubscriptionsIcon fontSize="small" />;
  if (name.includes("Pizza") || name.includes("Food"))
    return <FastfoodIcon fontSize="small" />;
  if (name.includes("Uber") || name.includes("Ride"))
    return <DirectionsCarIcon fontSize="small" />;
  if (name.includes("Salary") || name.includes("Deposit"))
    return <AttachMoneyIcon fontSize="small" />;
  if (name.includes("Apple") || name.includes("Store"))
    return <ShoppingBagIcon fontSize="small" />;
  return <LocalOfferIcon fontSize="small" />;
};

const TransactionTable = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <TableContainer sx={{ width: "100%", overflow: "hidden" }}>
      <Table aria-label="transaction table" sx={{ tableLayout: "fixed" }}>
        <TableHead>
          <TableRow>
            <TableCell
              sx={{
                color: "text.secondary",
                fontSize: "0.75rem",
                fontWeight: 500,
                borderBottom: "1px solid #f0f0f0",
                pb: 1,
                pl: 0,

                display: { xs: "none", sm: "table-cell" },
                width: "25%",
              }}
            >
              Date
            </TableCell>

            <TableCell
              sx={{
                color: "text.secondary",
                fontSize: "0.75rem",
                fontWeight: 500,
                borderBottom: "1px solid #f0f0f0",
                pb: 1,

                pl: { xs: 0, sm: 2 },
              }}
            >
              Receiver
            </TableCell>

            <TableCell
              align="right"
              sx={{
                color: "text.secondary",
                fontSize: "0.75rem",
                fontWeight: 500,
                borderBottom: "1px solid #f0f0f0",
                pb: 1,
                width: { xs: "25%", sm: "20%" },
              }}
            >
              Amount
            </TableCell>

            <TableCell
              sx={{
                width: "40px",
                borderBottom: "1px solid #f0f0f0",
                pb: 1,
                pr: 0,
              }}
            ></TableCell>
          </TableRow>
        </TableHead>

        <TableBody>
          {rows.map((row, index) => {
            const showDate = index === 0 || rows[index - 1].date !== row.date;

            return (
              <TableRow
                key={row.id}
                sx={{
                  "& td, & th": {
                    py: 1.5,
                    borderBottom: "none",
                  },
                  borderTop:
                    showDate && index !== 0 ? "1px solid #f0f0f0" : "none",
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
                      sx={{ display: "block", mt: 0.5 }}
                    >
                      {row.date}
                    </Typography>
                  )}
                </TableCell>

                <TableCell
                  component="th"
                  scope="row"
                  sx={{
                    verticalAlign: "top",
                    pl: { xs: 0, sm: 2 },
                  }}
                >
                  <Box sx={{ display: "flex", flexDirection: "column" }}>
                    <Box sx={{ display: { xs: "block", sm: "none" }, mb: 1 }}>
                      {showDate && (
                        <Typography
                          variant="caption"
                          fontWeight={700}
                          color="text.secondary"
                        >
                          {row.date}
                        </Typography>
                      )}
                    </Box>

                    <Box
                      sx={{ display: "flex", alignItems: "center", gap: 1.5 }}
                    >
                      <Avatar
                        variant="rounded"
                        sx={{
                          bgcolor: "grey.100",
                          color: "primary.main",
                          width: 32,
                          height: 32,
                          borderRadius: 2,
                        }}
                      >
                        {getIcon(row.name)}
                      </Avatar>
                      <Box sx={{ minWidth: 0, flex: 1 }}>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          color="text.primary"
                          noWrap
                          sx={{ fontSize: "0.875rem" }}
                        >
                          {row.name}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </TableCell>

                <TableCell align="right" sx={{ verticalAlign: "top" }}>
                  <Typography
                    variant="body2"
                    fontWeight={700}
                    sx={{
                      fontSize: "0.875rem",

                      mt: { xs: showDate ? 3.5 : 0.5, sm: 0.5 },
                      color: row.amount.includes("+")
                        ? "success.main"
                        : "text.primary",
                    }}
                  >
                    {row.amount}
                  </Typography>
                </TableCell>

                <TableCell align="right" sx={{ pr: 0, verticalAlign: "top" }}>
                  <IconButton
                    size="small"
                    onClick={handleMenuClick}
                    sx={{
                      color: "text.secondary",
                      p: 0.5,
                      mt: { xs: showDate ? 3 : 0, sm: 0 },
                    }}
                  >
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        slotProps={{
          paper: {
            elevation: 3,
            sx: {
              borderRadius: 2,
              minWidth: 120,
              overflow: "visible",
              filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
              mt: 1.5,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: "error.main" }}>
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
