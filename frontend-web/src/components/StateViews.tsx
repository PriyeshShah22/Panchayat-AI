import { Box, CircularProgress, Paper, Typography } from "@mui/material";

export function LoadingPanel({ label = "Loading…" }: { label?: string }) {
  return (
    <Paper sx={{ p: 4, display: "flex", alignItems: "center", gap: 2 }}>
      <CircularProgress size={20} />
      <Typography>{label}</Typography>
    </Paper>
  );
}

export function EmptyState({
  title,
  hint,
}: {
  title: string;
  hint?: string;
}) {
  return (
    <Paper sx={{ p: 4, textAlign: "center" }}>
      <Typography variant="h6">{title}</Typography>
      {hint && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {hint}
        </Typography>
      )}
    </Paper>
  );
}

export function ErrorPanel({ message }: { message: string }) {
  return (
    <Paper sx={{ p: 4, border: "1px solid", borderColor: "error.main" }}>
      <Box sx={{ color: "error.main" }}>
        <Typography variant="h6">Something went wrong</Typography>
        <Typography variant="body2">{message}</Typography>
      </Box>
    </Paper>
  );
}
