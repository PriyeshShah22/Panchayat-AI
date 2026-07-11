import {
  Box,
  Button,
  Chip,
  Stack,
  TextField,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from "@mui/material";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import LoginIcon from "@mui/icons-material/Login";
import LogoutIcon from "@mui/icons-material/Logout";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { DataTable, type Column } from "../components/Table";
import { LoadingPanel } from "../components/StateViews";
import type { Visitor } from "../types/api";

const STATUSES = ["pending", "approved", "rejected", "checked_in", "checked_out"];

export default function Visitors() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    society_id: 1,
    flat_id: 1,
    name: "",
    phone: "",
    purpose: "",
    vehicle_number: "",
  });

  const list = useQuery({
    queryKey: ["visitors"],
    queryFn: async () => (await api.get<Visitor[]>("/visitors/?limit=200")).data,
  });

  const create = useMutation({
    mutationFn: async (payload: any) => (await api.post("/visitors/", payload)).data,
    onSuccess: () => {
      enqueueSnackbar("Visitor registered", { variant: "success" });
      qc.invalidateQueries({ queryKey: ["visitors"] });
      setOpen(false);
      setForm({ society_id: 1, flat_id: 1, name: "", phone: "", purpose: "", vehicle_number: "" });
    },
  });

  const action = useMutation({
    mutationFn: async ({ id, kind }: { id: number; kind: string }) =>
      (await api.post(`/visitors/${id}/action`, { action: kind })).data,
    onSuccess: (_d, vars) => {
      enqueueSnackbar(`Visitor ${vars.kind} done`, { variant: "success" });
      qc.invalidateQueries({ queryKey: ["visitors"] });
    },
  });

  if (list.isLoading) return <LoadingPanel />;

  const cols: Column<Visitor>[] = [
    { key: "id", header: "ID", width: "70px" },
    { key: "name", header: "Name" },
    { key: "phone", header: "Phone" },
    { key: "purpose", header: "Purpose" },
    { key: "vehicle_number", header: "Vehicle" },
    {
      key: "status",
      header: "Status",
      render: (v) => <Chip size="small" label={v.status.replace("_", " ").toUpperCase()} variant="outlined" />,
    },
    { key: "created_at", header: "Created", render: (v) => new Date(v.created_at).toLocaleString() },
    {
      key: "actions",
      header: "Actions",
      render: (v) => (
        <Stack direction="row" spacing={1}>
          {v.status === "pending" && (
            <>
              <IconButton size="small" onClick={() => action.mutate({ id: v.id, kind: "approve" })}><CheckIcon fontSize="small" /></IconButton>
              <IconButton size="small" onClick={() => action.mutate({ id: v.id, kind: "reject" })}><CloseIcon fontSize="small" /></IconButton>
            </>
          )}
          {v.status === "approved" && (
            <IconButton size="small" onClick={() => action.mutate({ id: v.id, kind: "check_in" })}><LoginIcon fontSize="small" /></IconButton>
          )}
          {v.status === "checked_in" && (
            <IconButton size="small" onClick={() => action.mutate({ id: v.id, kind: "check_out" })}><LogoutIcon fontSize="small" /></IconButton>
          )}
        </Stack>
      ),
    },
  ];

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4">Visitors</Typography>
          <Typography variant="body2" color="text.secondary">
            Register, approve, and process visitor check-in/check-out.
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => setOpen(true)}>
          + Register Visitor
        </Button>
      </Stack>

      <DataTable data={list.data || []} columns={cols} searchKeys={["name", "status", "purpose"]} empty="No visitors yet" />

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Register a Visitor</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Visitor name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} fullWidth />
            <TextField label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} fullWidth />
            <TextField label="Purpose" value={form.purpose} onChange={(e) => setForm({ ...form, purpose: e.target.value })} fullWidth />
            <TextField label="Vehicle number" value={form.vehicle_number} onChange={(e) => setForm({ ...form, vehicle_number: e.target.value })} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!form.name || create.isPending}
            onClick={() => create.mutate(form)}
          >
            Register
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
