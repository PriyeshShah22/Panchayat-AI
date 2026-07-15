import { CircleRounded, CloseRounded, DoneAllRounded, NotificationsNoneRounded, ShieldRounded } from "@mui/icons-material";
import { Badge, Box, Button, Dialog, DialogContent, DialogTitle, Divider, IconButton, List, ListItemButton, ListItemIcon, ListItemText, Stack, Tooltip, Typography } from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { formatSocietyDateTime } from "../utils/dateTime";

type Notification = { id: number; kind: string; title: string; message: string; entity_type?: string | null; entity_id?: number | null; read_at?: string | null; created_at: string };

export default function NotificationInbox() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: async () => (await api.get<Notification[]>("/notifications/")).data, refetchInterval: 30_000 });
  const rows = notifications.data ?? [];
  const unread = rows.filter((row) => !row.read_at).length;
  const read = useMutation({ mutationFn: async (id: number) => api.post(`/notifications/${id}/read`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }) });
  const readAll = useMutation({ mutationFn: async () => api.post("/notifications/read-all"), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }) });
  const openNotification = (row: Notification) => {
    if (!row.read_at) read.mutate(row.id);
    if (row.entity_type === "visitor") navigate("/visitors");
    setOpen(false);
  };
  return <>
    <Tooltip title="Notifications"><IconButton aria-label={`${unread} unread notifications`} onClick={() => setOpen(true)}><Badge badgeContent={unread} color="error"><NotificationsNoneRounded /></Badge></IconButton></Tooltip>
    <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle><Stack direction="row" alignItems="center" justifyContent="space-between" gap={2}><Box><Typography variant="h5">Notifications</Typography><Typography variant="body2" color="text.secondary">Visitor approvals and gate updates</Typography></Box><IconButton aria-label="Close notifications" onClick={() => setOpen(false)}><CloseRounded /></IconButton></Stack></DialogTitle>
      <DialogContent dividers sx={{ p: 0 }}>
        {unread > 0 && <Stack direction="row" justifyContent="flex-end" sx={{ px: 2, py: 1 }}><Button size="small" startIcon={<DoneAllRounded />} onClick={() => readAll.mutate()}>Mark all read</Button></Stack>}
        <List disablePadding>{rows.map((row, index) => <Box key={row.id}>{index > 0 && <Divider />}<ListItemButton onClick={() => openNotification(row)} sx={{ py: 1.75, alignItems: "flex-start", bgcolor: row.read_at ? "transparent" : "action.hover" }}><ListItemIcon sx={{ minWidth: 42, color: row.kind === "visitor_approved" ? "success.main" : "warning.main", pt: .25 }}><ShieldRounded /></ListItemIcon><ListItemText primary={<Stack direction="row" alignItems="center" gap={1}><Typography fontWeight={row.read_at ? 700 : 900}>{row.title}</Typography>{!row.read_at && <CircleRounded color="primary" sx={{ fontSize: 9 }} />}</Stack>} secondary={<><Typography component="span" variant="body2" color="text.secondary">{row.message}</Typography><Typography component="span" display="block" variant="caption" color="text.disabled" sx={{ mt: .5 }}>{formatSocietyDateTime(row.created_at)} IST</Typography></>} /></ListItemButton></Box>)}
          {!notifications.isLoading && rows.length === 0 && <Box sx={{ py: 7, px: 2, textAlign: "center" }}><NotificationsNoneRounded sx={{ fontSize: 46, color: "text.disabled" }} /><Typography variant="h6" sx={{ mt: 1 }}>You’re all caught up</Typography><Typography color="text.secondary">New visitor updates will appear here.</Typography></Box>}
        </List>
      </DialogContent>
    </Dialog>
  </>;
}
