import {
  Box,
  Button,
  Chip,
  IconButton,
  Stack,
  TextField,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
} from "@mui/material";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { DataTable, type Column } from "../components/Table";
import { LoadingPanel } from "../components/StateViews";
import type { Complaint } from "../types/api";
import { useAuthStore } from "../store/auth";

const STATUS = ["open", "in_progress", "resolved", "closed", "escalated"];
const PRIORITY = ["low", "medium", "high", "urgent"];

export default function Complaints() {
  const qc = useQueryClient();
  const me = useAuthStore((s) => s.user);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    society_id: 1,
    flat_id: 1,
    priority: "medium",
  });
  const [editing, setEditing] = useState<Complaint | null>(null);

  const list = useQuery({
    queryKey: ["complaints"],
    queryFn: async () => (await api.get<Complaint[]>("/complaints/?limit=200")).data,
  });

  const create = useMutation({
    mutationFn: async (payload: any) => (await api.post("/complaints/", payload)).data,
    onSuccess: () => {
      enqueueSnackbar("Complaint created", { variant: "success" });
      qc.invalidateQueries({ queryKey: ["complaints"] });
      setDialogOpen(false);
      setForm({ title: "", description: "", society_id: 1, flat_id: 1, priority: "medium" });
    },
    onError: (err: any) => enqueueSnackbar(err?.response?.data?.detail || "Failed", { variant: "error" }),
  });

  const update = useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: any }) =>
      (await api.patch(`/complaints/${id}`, payload)).data,
    onSuccess: () => {
      enqueueSnackbar("Updated", { variant: "success" });
      qc.invalidateQueries({ queryKey: ["complaints"] });
      setEditing(null);
    },
  });

  const isPrivileged = (me?.roles || []).some((r) => ["admin", "committee"].includes(r.name)) || me?.is_superuser;

  if (list.isLoading) return <LoadingPanel />;

  const columns: Column<Complaint>[] = [
    { key: "id", header: "ID", width: "70px" },
    { key: "title", header: "Title" },
    {
      key: "priority",
      header: "Priority",
      render: (c) => <Chip size="small" label={c.priority.toUpperCase()} color={priorityColor(c.priority)} />,
    },
    {
      key: "status",
      header: "Status",
      render: (c) => <Chip size="small" label={c.status.replace("_", " ").toUpperCase()} variant="outlined" />,
    },
    {
      key: "ai_suggested_category",
      header: "AI category",
      render: (c) => (c.ai_suggested_category ? <Chip size="small" label={c.ai_suggested_category} /> : "—"),
    },
    { key: "created_at", header: "Created", render: (c) => new Date(c.created_at).toLocaleString() },
    {
      key: "actions",
      header: "Actions",
      render: (c) =>
        isPrivileged ? (
          <Stack direction="row" spacing={1}>
            <IconButton size="small" onClick={() => setEditing(c)}>
              <EditOutlinedIcon fontSize="small" />
            </IconButton>
          </Stack>
        ) : null,
    },
  ];

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4">Complaints</Typography>
          <Typography variant="body2" color="text.secondary">
            Track, classify, and resolve resident complaints.
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => setDialogOpen(true)}>
          + New Complaint
        </Button>
      </Stack>

      <DataTable
        data={list.data || []}
        columns={columns}
        searchKeys={["title", "status", "priority"]}
        empty="No complaints yet"
      />

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New Complaint</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              minRows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <TextField
              select
              label="Priority"
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              {PRIORITY.map((p) => (
                <MenuItem key={p} value={p}>{p}</MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!form.title || !form.description || create.isPending}
            onClick={() => create.mutate(form)}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(editing)} onClose={() => setEditing(null)} fullWidth maxWidth="xs">
        <DialogTitle>Update complaint #{editing?.id}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Status"
              value={editing?.status ?? "open"}
              onChange={(e) => setEditing((p) => (p ? { ...p, status: e.target.value } : p))}
            >
              {STATUS.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </TextField>
            <TextField
              select
              label="Priority"
              value={editing?.priority ?? "medium"}
              onChange={(e) => setEditing((p) => (p ? { ...p, priority: e.target.value } : p))}
            >
              {PRIORITY.map((p) => <MenuItem key={p} value={p}>{p}</MenuItem>)}
            </TextField>
            <TextField
              label="Assignee (user id)"
              type="number"
              value={editing?.assignee_id ?? ""}
              onChange={(e) => setEditing((p) => (p ? { ...p, assignee_id: Number(e.target.value) } : p))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditing(null)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={update.isPending}
            onClick={() =>
              editing &&
              update.mutate({
                id: editing.id,
                payload: {
                  status: editing.status,
                  priority: editing.priority,
                  assignee_id: editing.assignee_id || null,
                },
              })
            }
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function priorityColor(p: string): "default" | "info" | "warning" | "error" {
  switch (p) {
    case "urgent": return "error";
    case "high": return "warning";
    case "medium": return "info";
    default: return "default";
  }
}
