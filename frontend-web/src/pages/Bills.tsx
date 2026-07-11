import {
  Box,
  Button,
  Chip,
  IconButton,
  Stack,
  TextField,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { enqueueSnackbar } from "notistack";
import { api } from "../api/client";
import { DataTable, type Column } from "../components/Table";
import { LoadingPanel } from "../components/StateViews";
import type { Bill } from "../types/api";

export default function Bills() {
  const qc = useQueryClient();
  const [payOpen, setPayOpen] = useState<Bill | null>(null);
  const [payAmount, setPayAmount] = useState(0);
  const [payMethod, setPayMethod] = useState("upi");
  const [payRef, setPayRef] = useState("");

  const list = useQuery({
    queryKey: ["bills"],
    queryFn: async () => (await api.get<Bill[]>("/bills/?limit=200")).data,
  });

  const pay = useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: any }) =>
      (await api.post(`/bills/${id}/pay`, payload)).data,
    onSuccess: () => {
      enqueueSnackbar("Payment recorded", { variant: "success" });
      qc.invalidateQueries({ queryKey: ["bills"] });
      setPayOpen(null);
    },
    onError: (err: any) => enqueueSnackbar(err?.response?.data?.detail || "Payment failed", { variant: "error" }),
  });

  if (list.isLoading) return <LoadingPanel />;

  const cols: Column<Bill>[] = [
    { key: "bill_number", header: "Bill #" },
    { key: "title", header: "Title" },
    { key: "total_amount", header: "Total (₹)", render: (b) => b.total_amount.toLocaleString("en-IN") },
    { key: "paid_amount", header: "Paid (₹)", render: (b) => b.paid_amount.toLocaleString("en-IN") },
    {
      key: "outstanding",
      header: "Outstanding",
      render: (b) => {
        const o = b.total_amount - b.paid_amount;
        return (
          <Chip
            size="small"
            color={o > 0 ? "warning" : "success"}
            label={`₹ ${o.toLocaleString("en-IN")}`}
          />
        );
      },
    },
    {
      key: "status",
      header: "Status",
      render: (b) => <Chip size="small" label={b.status.toUpperCase()} variant="outlined" />,
    },
    { key: "due_date", header: "Due", render: (b) => b.due_date },
    {
      key: "actions",
      header: "Actions",
      render: (b) => (
        <Stack direction="row" spacing={1}>
          <IconButton
            size="small"
            onClick={async () => {
              try {
                const res = await api.get(`/bills/${b.id}/pdf`, { responseType: "blob" });
                const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
                const a = document.createElement("a");
                a.href = url;
                a.download = `${b.bill_number}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
              } catch (e: any) {
                enqueueSnackbar("Could not download PDF", { variant: "error" });
              }
            }}
          >
            <DownloadIcon fontSize="small" />
          </IconButton>
          {b.status !== "paid" && (
            <Button size="small" variant="outlined" onClick={() => { setPayOpen(b); setPayAmount(Math.max(0, b.total_amount - b.paid_amount)); }}>
              Pay
            </Button>
          )}
        </Stack>
      ),
    },
  ];

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4">Bills & Maintenance</Typography>
          <Typography variant="body2" color="text.secondary">
            View, pay, and download maintenance invoices.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" onClick={() => api.get("/reports/bills.xlsx", { responseType: "blob" }).then((r) => {
            const url = window.URL.createObjectURL(new Blob([r.data]));
            const a = document.createElement("a"); a.href = url; a.download = "bills.xlsx"; a.click();
          })}>
            Export Excel
          </Button>
        </Stack>
      </Stack>
      <DataTable data={list.data || []} columns={cols} searchKeys={["bill_number", "title", "status"]} empty="No bills" />

      <Dialog open={Boolean(payOpen)} onClose={() => setPayOpen(null)} fullWidth maxWidth="xs">
        <DialogTitle>Pay bill {payOpen?.bill_number}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Amount"
              type="number"
              value={payAmount}
              onChange={(e) => setPayAmount(Number(e.target.value))}
              fullWidth
            />
            <TextField
              label="Method"
              select
              SelectProps={{ native: true }}
              value={payMethod}
              onChange={(e) => setPayMethod(e.target.value)}
              fullWidth
            >
              <option value="upi">UPI</option>
              <option value="card">Card</option>
              <option value="cash">Cash</option>
              <option value="netbanking">Netbanking</option>
              <option value="cheque">Cheque</option>
            </TextField>
            <TextField
              label="Transaction reference"
              value={payRef}
              onChange={(e) => setPayRef(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPayOpen(null)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!payAmount || payAmount <= 0 || pay.isPending}
            onClick={() =>
              payOpen &&
              pay.mutate({
                id: payOpen.id,
                payload: { amount: payAmount, method: payMethod, transaction_ref: payRef || null },
              })
            }
          >
            Confirm Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
