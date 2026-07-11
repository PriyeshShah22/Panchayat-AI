import {
  Box,
  Button,
  Chip,
  Stack,
  TextField,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import PushPinIcon from "@mui/icons-material/PushPin";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { enqueueSnackbar } from "notistack";
import dayjs from "dayjs";
import { api } from "../api/client";
import { LoadingPanel } from "../components/StateViews";
import type { Notice } from "../types/api";

export default function Notices() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    society_id: 1,
    title: "",
    body: "",
    is_pinned: false,
  });

  const list = useQuery({
    queryKey: ["notices"],
    queryFn: async () => (await api.get<Notice[]>("/notices/")).data,
  });

  const create = useMutation({
    mutationFn: async (payload: any) => (await api.post("/notices/", payload)).data,
    onSuccess: () => {
      enqueueSnackbar("Notice published", { variant: "success" });
      qc.invalidateQueries({ queryKey: ["notices"] });
      setOpen(false);
    },
    onError: (err: any) => enqueueSnackbar(err?.response?.data?.detail || "Failed", { variant: "error" }),
  });

  if (list.isLoading) return <LoadingPanel />;

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4">Notice Board</Typography>
          <Typography variant="body2" color="text.secondary">
            Announcements and important society updates.
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => setOpen(true)}>+ New Notice</Button>
      </Stack>

      <Stack spacing={2}>
        {(list.data || []).map((n) => (
          <Paper key={n.id} sx={{ p: 2, borderRadius: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {n.is_pinned && <PushPinIcon fontSize="small" sx={{ mr: 1, color: "primary.main" }} />}
                  {n.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {dayjs(n.published_at).format("DD MMM YYYY, HH:mm")} · audience: {n.audience}
                </Typography>
                <Typography variant="body1" sx={{ mt: 1, whiteSpace: "pre-wrap" }}>
                  {n.body}
                </Typography>
              </Box>
              <Chip label={n.is_pinned ? "Pinned" : "Regular"} size="small" />
            </Stack>
          </Paper>
        ))}
      </Stack>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Publish Notice</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" fullWidth value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <TextField label="Body" fullWidth multiline minRows={4} value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
            <Stack direction="row" spacing={1} alignItems="center">
              <input
                id="pin"
                type="checkbox"
                checked={form.is_pinned}
                onChange={(e) => setForm({ ...form, is_pinned: e.target.checked })}
              />
              <label htmlFor="pin">Pin this notice</label>
            </Stack>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!form.title || !form.body || create.isPending} onClick={() => create.mutate(form)}>
            Publish
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
