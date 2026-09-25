import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";

import Dashboard from "./pages/Dashboard";
import Transliterate from "./pages/Transliterate";  
import History from "./pages/History";
import Settings from "./pages/Settings";

function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "light";
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add(
        "dark-theme"
      );
    } else {
      document.documentElement.classList.remove(
        "dark-theme"
      );
    }

    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((currentTheme) =>
      currentTheme === "light"
        ? "dark"
        : "light"
    );
  };

  return (
    <BrowserRouter>

      <AppLayout
        theme={theme}
        onToggleTheme={toggleTheme}
      >

        <Routes>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/transliterate"
            element={<Transliterate />}
          />

          <Route
            path="/history"
            element={<History />}
          />

          <Route
            path="/settings"
            element={<Settings />}
          />

        </Routes>

      </AppLayout>

    </BrowserRouter>
  );
}

export default App;