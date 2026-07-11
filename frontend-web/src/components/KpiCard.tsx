import { Box, Paper, Stack, Typography } from "@mui/material";
import type { ReactNode } from "react";

export function KpiCard({
  title,
  value,
  icon,
  color = "primary.main",
}: {
  title: string;
  value: ReactNode;
  icon?: ReactNode;
  color?: string;
}) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        bgcolor: "background.paper",
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 3,
      }}
    >
      <Stack direction="row" spacing={2} alignItems="center">
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            color,
            bgcolor: (t) =>
              t.palette.mode === "dark" ? "rgba(255,255,255,0.06)" : `${color}14`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 24,
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h5" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
            {value}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
}
