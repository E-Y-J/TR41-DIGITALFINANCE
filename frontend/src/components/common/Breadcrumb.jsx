import { Breadcrumbs, Link, Typography } from "@mui/material";
import { useLocation, Link as RouterLink } from "react-router-dom";

import NavigateNextIcon from "@mui/icons-material/NavigateNext";

const Breadcrumb = () => {
  const location = useLocation();
  const pathnames = location.pathname.split("/").filter((x) => x);

  if (pathnames.length === 0) {
    return null;
  }

  return (
    <Breadcrumbs
      separator={
        <NavigateNextIcon sx={{ fontSize: { xs: "1rem", sm: "1.25rem" } }} />
      }
      aria-label="breadcrumb"
      sx={{
        "& .MuiBreadcrumbs-ol": {
          alignItems: "center",
        },
      }}
    >
      {pathnames.map((value, index) => {
        const last = index === pathnames.length - 1;
        const to = `/${pathnames.slice(0, index + 1).join("/")}`;

        const text = value.replace(/-/g, " ");

        return last ? (
          <Typography
            key={to}
            color="text.primary"
            variant="body2"
            fontWeight={600}
            sx={{
              fontSize: { xs: "0.75rem", sm: "0.875rem" },
              textTransform: "capitalize",
            }}
          >
            {text}
          </Typography>
        ) : (
          <Link
            component={RouterLink}
            underline="hover"
            color="inherit"
            to={to}
            key={to}
            variant="body2"
            sx={{
              color: "text.secondary",
              textTransform: "capitalize",
              fontSize: { xs: "0.75rem", sm: "0.875rem" },
              "&:hover": { color: "primary.main" },
            }}
          >
            {text}
          </Link>
        );
      })}
    </Breadcrumbs>
  );
};

export default Breadcrumb;
