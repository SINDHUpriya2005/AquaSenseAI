import { NavLink } from "react-router-dom";
import { IconChart, IconClock, IconDroplet, IconFlask, IconGauge } from "./Icons";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: IconGauge },
  { to: "/purifiers", label: "Purifiers", icon: IconDroplet },
  { to: "/readings", label: "Water Readings", icon: IconFlask },
  { to: "/analytics", label: "Analytics", icon: IconChart },
  { to: "/history", label: "History", icon: IconClock },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-mark">
          <IconDroplet width={18} height={18} />
        </span>
        <div>
          <div className="sidebar__brand-name">AquaSense</div>
          <div className="sidebar__brand-sub">AI Filter Prognostics</div>
        </div>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => "sidebar__link" + (isActive ? " sidebar__link--active" : "")}
          >
            <Icon width={18} height={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="sidebar__footer-card">
          <div className="sidebar__footer-title">Sensor-ready architecture</div>
          <p>Running on simulated readings today. Point an ESP32 feed at the readings API whenever hardware is connected.</p>
        </div>
      </div>
    </aside>
  );
}
