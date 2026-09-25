import Header from "./Header";
import Sidebar from "./Sidebar";

function AppLayout({
  children,
  theme,
  onToggleTheme,
}) {
  return (
    <div className="app-shell">

      <Sidebar />

      <div className="app-content">

        <Header
          theme={theme}
          onToggleTheme={onToggleTheme}
        />

        <main className="main-content">
          {children}
        </main>

      </div>

    </div>
  );
}

export default AppLayout;