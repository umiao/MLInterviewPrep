import { NavLink } from "react-router-dom";

const navItems: { to: string; label: string; separator?: boolean }[] = [
  { to: "/", label: "Dashboard" },
  { to: "/quick-index", label: "Quick Index" },
  { to: "/problems", label: "LeetCode" },
  { to: "/framework", label: "Framework" },
  { to: "/system-design", label: "System Design" },
  { to: "/behavioral", label: "Behavioral" },
  { to: "/questions", label: "Questions" },
  { to: "/companies", label: "Companies" },
  { to: "/radio", label: "Study Radio" },
  { to: "/analytics", label: "Analytics" },
  { to: "/settings", label: "Settings" },
  { to: "/baking", label: "Baking Studio", separator: true },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-gray-900 text-gray-300 flex flex-col min-h-screen">
      <div className="px-5 py-6 text-lg font-bold text-white tracking-tight">
        ML Interview Prep
      </div>
      <nav className="flex flex-col gap-1 px-3">
        {navItems.map((item) => (
          <div key={item.to}>
            {item.separator && (
              <div className="border-t border-gray-700 mt-2 pt-2" />
            )}
            <NavLink
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm transition-colors block ${
                  isActive
                    ? "bg-gray-700 text-white font-medium"
                    : "hover:bg-gray-800 hover:text-white"
                }`
              }
            >
              {item.label}
            </NavLink>
          </div>
        ))}
      </nav>
    </aside>
  );
}
