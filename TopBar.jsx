import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { usePurifiers } from "../context/PurifierContext";
import { IconChevronDown, IconLogout } from "./Icons";

const PAGE_TITLES = {
  "/dashboard": ["Dashboard", "A live read on every filter's health and remaining life."],
  "/purifiers": ["Purifiers", "Register and manage the units on your account."],
  "/readings": ["Water Readings", "Log water-quality and usage data for a purifier."],
  "/analytics": ["Analytics", "Trends across water quality and filter degradation."],
  "/history": ["History", "Every prediction the AI model has generated over time."],
};

export default function TopBar() {
  const { user, logout } = useAuth();
  const { purifiers, selectedId, setSelectedId, loading } = usePurifiers();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const [title, subtitle] = PAGE_TITLES[location.pathname] || ["AquaSense AI", ""];

  const initials = (user?.name || "?")
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="topbar">
      <div>
        <h1 className="topbar__title">{title}</h1>
        {subtitle ? <p className="topbar__subtitle text-secondary">{subtitle}</p> : null}
      </div>

      <div className="topbar__actions">
        {!loading && purifiers.length > 0 && (
          <div className="purifier-select">
            <select
              value={selectedId || ""}
              onChange={(e) => setSelectedId(e.target.value)}
              aria-label="Select active purifier"
            >
              {purifiers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <IconChevronDown width={16} height={16} />
          </div>
        )}

        <div className="user-menu">
          <button className="user-menu__trigger" onClick={() => setMenuOpen((v) => !v)}>
            <span className="user-menu__avatar">{initials}</span>
          </button>
          {menuOpen && (
            <div className="user-menu__dropdown" onMouseLeave={() => setMenuOpen(false)}>
              <div className="user-menu__name">{user?.name}</div>
              <div className="user-menu__email text-secondary">{user?.email}</div>
              <button
                className="user-menu__logout"
                onClick={() => {
                  logout();
                  navigate("/login");
                }}
              >
                <IconLogout width={16} height={16} />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
