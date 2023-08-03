"use client";

import { AppBar, Toolbar, Typography } from "@mui/material";

export default function TitleBar() {
  return (
    <AppBar
      position="fixed"
      sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Catalog API
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
