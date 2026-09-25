import {
  LayoutDashboard,
  Languages,
  History,
  Settings,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigationItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/",
  },
  {
    label: "Transliterate",
    icon: Languages,
    path: "/transliterate",
  },
  {
    label: "History",
    icon: History,
    path: "/history",
  },
  {
    label: "Settings",
    icon: Settings,
    path: "/settings",
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Languages size={22} />
        </div>

        <div>
          <h1>Transliterate</h1>
          <span>Enterprise</span>
        </div>
      </div>

      <nav className="sidebar-navigation">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-item ${
                  isActive ? "sidebar-item-active" : ""
                }`
              }
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span>Universal Transliteration</span>
        <small>v1.0</small>
      </div>
    </aside>
  );
}

export default Sidebar;