import {
  Moon,
  Sun,
} from "lucide-react";

function Header({
  theme,
  onToggleTheme,
}) {
  return (
    <header className="header">

      <div className="header-title">
        <span className="header-eyebrow">
          Workspace
        </span>

        <h2>
          Universal Transliteration
        </h2>
      </div>

      <div className="header-actions">

        {/* Theme */}

        <button
          type="button"
          className="header-icon-button"
          onClick={onToggleTheme}
          aria-label={
            theme === "light"
              ? "Switch to dark theme"
              : "Switch to light theme"
          }
          title={
            theme === "light"
              ? "Switch to dark theme"
              : "Switch to light theme"
          }
        >
          {theme === "light" ? (
            <Moon size={18} />
          ) : (
            <Sun size={18} />
          )}
        </button>

      </div>

    </header>
  );
}

export default Header;