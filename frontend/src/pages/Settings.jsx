import { useState } from "react";

function Settings() {
  const [defaultLanguage, setDefaultLanguage] =
    useState(() => {
      return (
        localStorage.getItem("defaultLanguage") ||
        "auto"
      );
    });

  const [automaticLanguageDetection, setAutomaticLanguageDetection] =
    useState(() => {
      const savedValue = localStorage.getItem(
        "automaticLanguageDetection"
      );

      return savedValue === null
        ? true
        : savedValue === "true";
    });

  const handleLanguageChange = (event) => {
    const language = event.target.value;

    setDefaultLanguage(language);

    localStorage.setItem(
      "defaultLanguage",
      language
    );
  };

  const handleAutomaticDetectionChange = (event) => {
    const enabled = event.target.checked;

    setAutomaticLanguageDetection(enabled);

    localStorage.setItem(
      "automaticLanguageDetection",
      String(enabled)
    );
  };

  return (
    <section className="settings-page">
      <div className="page-heading">
        <span className="page-eyebrow">
          Workspace
        </span>

        <h1>Settings</h1>

        <p>
          Manage your transliteration workspace preferences.
        </p>
      </div>

      <div className="settings-section">
        <div className="settings-section-header">
          <h2>General</h2>

          <p>
            Configure the basic behavior of the application.
          </p>
        </div>

        <div className="settings-card">
          <div className="settings-row">
            <div>
              <h3>Default Language</h3>

              <p>
                Choose the language used when automatic
                detection is not selected.
              </p>
            </div>

            <select
              value={defaultLanguage}
              onChange={handleLanguageChange}
            >
              <option value="auto">
                Auto Detection
              </option>

              <option value="telugu">
                Telugu
              </option>

              <option value="hindi">
                Hindi
              </option>

              <option value="tamil">
                Tamil
              </option>

              <option value="bengali">
                Bengali
              </option>

              <option value="kannada">
                Kannada
              </option>

              <option value="gujarati">
                Gujarati
              </option>

              <option value="punjabi">
                Punjabi
              </option>

              <option value="marathi">
                Marathi
              </option>

              <option value="odia">
                Odia
              </option>
            </select>
          </div>
        </div>
      </div>

      {/* =========================
          TRANSLITERATION SETTINGS
          ========================= */}

      <div className="settings-section">
        <div className="settings-section-header">
          <h2>Transliteration</h2>

          <p>
            Configure how language detection works during
            transliteration.
          </p>
        </div>

        <div className="settings-card">
          <div className="settings-row">
            <div>
              <h3>
                Automatic Language Detection
              </h3>

              <p>
                Automatically detect the input language
                when Auto Detection is selected.
              </p>
            </div>

            <label className="settings-toggle">
              <input
                type="checkbox"
                checked={automaticLanguageDetection}
                onChange={
                  handleAutomaticDetectionChange
                }
              />

              <span className="settings-toggle-slider" />
            </label>
          </div>
        </div>
      </div>

      <div className="settings-section">
        <div className="settings-section-header">
          <h2>About</h2>

          <p>
            Information about this transliteration workspace.
          </p>
        </div>

        <div className="settings-card">
          <div className="settings-row">
            <div>
              <h3>Supported File Types</h3>

              <p>
                Text, PDF, DOCX, PNG, JPG and JPEG files.
              </p>
            </div>
          </div>

          <div className="settings-row">
            <div>
              <h3>Language Detection</h3>

              <p>
                Language and script detection are handled
                automatically by the backend.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Settings;