import React from "react";
import { Grid, Grow, Paper, List, Box, Divider } from "@mui/material";
import BudgetCard from "./BudgetCard";
import BudgetRow from "./BudgetRow";

const CategoryGrid = ({ items, viewMode, onEdit, onDelete }) => {
  if (viewMode === "grid") {
    return (
      <Grid
        container
        spacing={2.5}
        alignItems="stretch"
        sx={{ width: "100%", margin: 0 }}
      >
        {items.map((budget, index) => (
          <Grid
            item
            key={budget.id}
            xs={12}
            sm={6}
            md={4}
            lg={4}
            sx={{ display: "flex" }}
          >
            <Grow in timeout={(index % 3) * 150}>
              <Box sx={{ width: "100%", display: "flex" }}>
                <BudgetCard
                  budget={budget}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              </Box>
            </Grow>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Paper
      variant="outlined"
      sx={{
        width: "100%",
        borderRadius: 4,
        borderColor: "divider",
        bgcolor: "transparent",
        overflow: "hidden",
      }}
    >
      <List disablePadding>
        {items.map((budget, idx) => (
          <React.Fragment key={budget.id}>
            <BudgetRow budget={budget} onEdit={onEdit} onDelete={onDelete} />
            {idx < items.length - 1 && <Divider sx={{ mx: 3, opacity: 0.5 }} />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default CategoryGrid;
