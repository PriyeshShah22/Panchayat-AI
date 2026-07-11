import { Box, Paper, Stack, Table as MuiTable, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography, TextField, MenuItem, Select, FormControl, InputLabel } from "@mui/material";
import { useMemo, useState } from "react";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  render?: (row: T) => React.ReactNode;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  searchKeys,
  empty = "No records",
}: {
  data: T[];
  columns: Column<T>[];
  searchKeys?: (keyof T)[];
  empty?: string;
}) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<string>("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const filtered = useMemo(() => {
    let rows = data;
    if (query && searchKeys?.length) {
      const q = query.toLowerCase();
      rows = rows.filter((r) =>
        searchKeys.some((k) => String(r[k] ?? "").toLowerCase().includes(q))
      );
    }
    if (sortKey) {
      rows = [...rows].sort((a, b) => {
        const av = a[sortKey];
        const bv = b[sortKey];
        const cmp = String(av ?? "").localeCompare(String(bv ?? ""));
        return sortDir === "asc" ? cmp : -cmp;
      });
    }
    return rows;
  }, [data, query, sortKey, sortDir, searchKeys]);

  return (
    <Paper sx={{ p: 2 }}>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          label="Search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Sort by</InputLabel>
          <Select
            label="Sort by"
            value={sortKey}
            onChange={(e) => setSortKey(String(e.target.value))}
          >
            <MenuItem value="">None</MenuItem>
            {columns.map((c) => (
              <MenuItem key={String(c.key)} value={String(c.key)}>
                {c.header}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl size="small">
          <Select
            value={sortDir}
            onChange={(e) => setSortDir(e.target.value as any)}
          >
            <MenuItem value="asc">Ascending</MenuItem>
            <MenuItem value="desc">Descending</MenuItem>
          </Select>
        </FormControl>
      </Stack>
      <TableContainer>
        <MuiTable size="small">
          <TableHead>
            <TableRow>
              {columns.map((c) => (
                <TableCell key={String(c.key)} sx={{ fontWeight: 700, width: c.width }}>
                  {c.header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length}>
                  <Box sx={{ p: 3, textAlign: "center" }}>
                    <Typography color="text.secondary">{empty}</Typography>
                  </Box>
                </TableCell>
              </TableRow>
            )}
            {filtered.map((row, idx) => (
              <TableRow hover key={idx}>
                {columns.map((c) => (
                  <TableCell key={String(c.key)}>
                    {c.render ? c.render(row) : String(row[c.key as keyof T] ?? "")}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </MuiTable>
      </TableContainer>
    </Paper>
  );
}
