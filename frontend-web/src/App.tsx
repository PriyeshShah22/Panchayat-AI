import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Complaints from "./pages/Complaints";
import Bills from "./pages/Bills";
import Visitors from "./pages/Visitors";
import Notices from "./pages/Notices";
import Residents from "./pages/Residents";
import AI from "./pages/AI";
import Admin from "./pages/Admin";
import AppLayout from "./components/AppLayout";
import { useAuthStore } from "./store/auth";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.accessToken);
  const location = useLocation();
  if (!token) return <Navigate to="/login" state={{ from: location }} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="complaints" element={<Complaints />} />
        <Route path="bills" element={<Bills />} />
        <Route path="visitors" element={<Visitors />} />
        <Route path="notices" element={<Notices />} />
        <Route path="residents" element={<Residents />} />
        <Route path="ai" element={<AI />} />
        <Route path="admin" element={<Admin />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
