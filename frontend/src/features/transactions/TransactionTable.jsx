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
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  alpha,
  useTheme,
} from "@mui/material";

// Icons
import MoreVertIcon from "@mui/icons-material/MoreVert";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ShoppingBagIcon from "@mui/icons-material/ShoppingBag";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import FastfoodIcon from "@mui/icons-material/Fastfood";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import VolunteerActivismIcon from "@mui/icons-material/VolunteerActivism";
import TheaterComedyIcon from "@mui/icons-material/TheaterComedy";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import MedicalServicesIcon from "@mui/icons-material/MedicalServices";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import GavelIcon from "@mui/icons-material/Gavel";

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

  // Charity & Donations
  if (lowerName.includes("charity") || lowerName.includes("donation")) {
    return <VolunteerActivismIcon fontSize="small" />;
  }

  // Entertainment & Recreation
  else if (
    lowerName.includes("entertainment") ||
    lowerName.includes("recreation")
  ) {
    return <TheaterComedyIcon fontSize="small" />;
  }
  // Financial Services
  else if (lowerName.includes("financial")) {
    return <AccountBalanceIcon fontSize="small" />;
  }

  // Food & Dining
  else if (lowerName.includes("food") || lowerName.includes("dining")) {
    return <FastfoodIcon fontSize="small" />;
  }

  // Government & Legal
  else if (lowerName.includes("government") || lowerName.includes("legal")) {
    return <GavelIcon fontSize="small" />;
  }

  // Healthcare & Medical
  else if (lowerName.includes("health") || lowerName.includes("medical")) {
    return <MedicalServicesIcon fontSize="small" />;
  }

  // Income
  else if (lowerName.includes("income") || lowerName.includes("salary")) {
    return <AttachMoneyIcon fontSize="small" />;
  }

  // Shopping & Retail
  else if (lowerName.includes("shopping") || lowerName.includes("retail")) {
    return <ShoppingBagIcon fontSize="small" />;
  }

  // Transportation
  else if (lowerName.includes("transportation")) {
    return <DirectionsCarIcon fontSize="small" />;
  }

  // Utilities & Services
  else if (lowerName.includes("utilit") || lowerName.includes("services")) {
    return <LightbulbIcon fontSize="small" />;
  }

  // Fallback Icon
  else {
    return <LocalOfferIcon fontSize="small" />;
  }
};

const TransactionTable = ({ data }) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const headerStyle = {
    color: "text.secondary",
    fontSize: "0.825rem",
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "1px",
    borderBottom: "1px solid",
    borderColor: "divider",
    pb: 1,
  };

  return (
    <TableContainer sx={{ width: "100%", overflow: "hidden" }}>
      <Table aria-label="transaction table" sx={{ tableLayout: "fixed" }}>
        <TableHead>
          <TableRow>
            <TableCell
              sx={{
                ...headerStyle,
                pl: 0,
                display: { xs: "none", sm: "table-cell" },
                width: "25%",
              }}
            >
              Date
            </TableCell>
            <TableCell sx={{ ...headerStyle, pl: { xs: 0, sm: 2 } }}>
              Merchant
            </TableCell>
            <TableCell
              align="right"
              sx={{ ...headerStyle, width: { xs: "25%", sm: "20%" } }}
            >
              Amount
            </TableCell>
            <TableCell sx={{ ...headerStyle, width: "40px", pr: 0 }} />
          </TableRow>
        </TableHead>

        <TableBody>
          {data && data.length > 0 ? (
            data.map((row, index) => {
              // Date Grouping Logic
              const currentFormattedDate = formatDate(row.date);
              const prevFormattedDate =
                index > 0 ? formatDate(data[index - 1].date) : null;
              const showDate =
                index === 0 || currentFormattedDate !== prevFormattedDate;

              // Income vs Expense Logic
              const isIncome = row.transaction_type === "income";
              const amountColor = isIncome ? "success.main" : "text.primary";
              const amountPrefix = isIncome ? "+" : "";

              // Format Amount as Currency
              const formattedAmount = `${amountPrefix}$${parseFloat(row.amount).toFixed(2)}`;

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
                    borderColor: "divider",
                    transition: "background-color 0.2s",
                    "&:hover": {
                      bgcolor: alpha(theme.palette.primary.main, 0.04),
                    },
                  }}
                >
                  {/* DATE CELL  */}
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

                  {/* MERCHANT INFO CELL */}
                  <TableCell
                    component="th"
                    scope="row"
                    sx={{
                      verticalAlign: "top",
                      pl: { xs: 0, sm: 2 },
                    }}
                  >
                    <Box sx={{ display: "flex", flexDirection: "column" }}>
                      {/* Mobile Date Header */}
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
                          gap: 1.5,
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
                          }}
                        >
                          {getIcon(row.category_name)}
                        </Avatar>
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography
                            variant="body2"
                            fontWeight={600}
                            color="text.primary"
                            noWrap
                            sx={{ fontSize: "0.875rem" }}
                          >
                            {row.merchant_name || "Unknown Merchant"}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: "block", mt: -0.2 }}
                          >
                            {row.category_name || "General"}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </TableCell>

                  {/* AMOUNT CELL */}
                  <TableCell align="right" sx={{ verticalAlign: "top" }}>
                    <Typography
                      variant="body2"
                      fontWeight={700}
                      sx={{
                        fontSize: "0.875rem",
                        mt: { xs: showDate ? 3.5 : 0.5, sm: 0.5 },
                        color: amountColor,
                      }}
                    >
                      {formattedAmount}
                    </Typography>
                  </TableCell>

                  {/* ACTIONS CELL */}
                  <TableCell align="right" sx={{ pr: 0, verticalAlign: "top" }}>
                    <IconButton
                      disableFocusRipple
                      disableRipple
                      disableTouchRipple
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
            })
          ) : (
            <TableRow>
              <TableCell
                colSpan={4}
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

      {/* Menu Logic */}
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
