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

export const getIcon = (categoryName = "") => {
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

export const getStatusLabel = (status = "completed") => {
  const s = status.toLowerCase();

  if (s === "completed" || s === "posted") {
    return "Posted";
  } else if (s === "pending") {
    return "Pending";
  } else {
    return "Failed";
  }
};
