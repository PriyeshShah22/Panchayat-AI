import { createTheme } from "@mui/material/styles";
import type { PaletteMode } from "@mui/material";

export function buildTheme(mode: PaletteMode) {
  return createTheme({
    palette: {
      mode,
      primary: { main: mode === "dark" ? "#82b1ff" : "#0F62FE" },
      secondary: { main: "#7C4DFF" },
      background: {
        default: mode === "dark" ? "#0E1116" : "#F5F7FA",
        paper: mode === "dark" ? "#161B22" : "#FFFFFF",
      },
    },
    shape: { borderRadius: 12 },
    typography: {
      fontFamily:
        '"Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
      h4: { fontWeight: 700 },
      h5: { fontWeight: 700 },
      h6: { fontWeight: 600 },
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: "none" },
        },
      },
      MuiButton: {
        styleOverrides: { root: { textTransform: "none", fontWeight: 600 } },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: mode === "dark" ? "#0F62FE" : "#0F62FE",
          },
        },
      },
    },
  });
}
