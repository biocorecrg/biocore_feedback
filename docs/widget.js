/**
 * Biocore Feedback Widget (<biocore-feedback>)
 * Standalone Web Component encapsulated in Shadow DOM.
 * Works across any framework or static HTML page.
 */
(function () {
  // Determine the default script base URL from current script src
  const currentScript = document.currentScript;
  let defaultApiUrl = "";
  if (currentScript && currentScript.src) {
    try {
      const scriptUrl = new URL(currentScript.src);
      defaultApiUrl = `${scriptUrl.origin}/api/feedback`;
    } catch (e) {
      // Fallback
    }
  }

  const template = document.createElement("template");
  template.innerHTML = `
    <style>
      :host {
        --bf-primary: #0d6efd;
        --bf-primary-hover: #0b5ed7;
        --bf-bg: #ffffff;
        --bf-text: #212529;
        --bf-muted: #6c757d;
        --bf-border: #dee2e6;
        --bf-success: #198754;
        --bf-danger: #dc3545;
        --bf-radius: 8px;
        --bf-shadow: 0 10px 25px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.1);
        --bf-font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999;
        font-family: var(--bf-font);
        box-sizing: border-box;
      }

      *, *::before, *::after {
        box-sizing: inherit;
      }

      /* Trigger Button */
      .bf-trigger {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: var(--bf-primary);
        color: #ffffff;
        border: none;
        border-radius: 50px;
        padding: 10px 18px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: var(--bf-shadow);
        transition: transform 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease;
        outline: none;
        user-select: none;
      }

      .bf-trigger:hover {
        background-color: var(--bf-primary-hover);
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
      }

      .bf-trigger:active {
        transform: translateY(0);
      }

      .bf-icon {
        width: 16px;
        height: 16px;
        fill: currentColor;
      }

      /* Modal Popover */
      .bf-modal {
        position: absolute;
        bottom: 54px;
        right: 0;
        width: 330px;
        max-width: 90vw;
        background: var(--bf-bg);
        border: 1px solid var(--bf-border);
        border-radius: var(--bf-radius);
        box-shadow: var(--bf-shadow);
        padding: 16px 18px;
        display: none;
        flex-direction: column;
        color: var(--bf-text);
        animation: bf-fade-in 0.18s ease-out;
      }

      .bf-modal.open {
        display: flex;
      }

      @keyframes bf-fade-in {
        from {
          opacity: 0;
          transform: translateY(8px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .bf-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--bf-border);
      }

      .bf-title {
        font-size: 15px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .bf-close {
        background: none;
        border: none;
        font-size: 18px;
        line-height: 1;
        cursor: pointer;
        color: var(--bf-muted);
        padding: 2px 6px;
        border-radius: 4px;
      }

      .bf-close:hover {
        color: var(--bf-text);
        background: #f1f3f5;
      }

      /* Form Elements */
      .bf-form-group {
        margin-bottom: 12px;
      }

      .bf-label {
        display: block;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
        color: var(--bf-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .bf-app-badge {
        display: inline-block;
        background-color: #e9ecef;
        color: #495057;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        word-break: break-all;
      }

      .bf-input, .bf-textarea {
        width: 100%;
        padding: 8px 10px;
        border: 1px solid var(--bf-border);
        border-radius: 6px;
        font-family: inherit;
        font-size: 13px;
        color: var(--bf-text);
        background-color: #ffffff;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
      }

      .bf-input:focus, .bf-textarea:focus {
        border-color: var(--bf-primary);
        outline: none;
        box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
      }

      .bf-textarea {
        resize: vertical;
        min-height: 75px;
        max-height: 180px;
      }

      /* Submit button */
      .bf-submit {
        width: 100%;
        background-color: var(--bf-primary);
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 9px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.15s ease;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
      }

      .bf-submit:hover:not(:disabled) {
        background-color: var(--bf-primary-hover);
      }

      .bf-submit:disabled {
        opacity: 0.65;
        cursor: not-allowed;
      }

      /* Alert message */
      .bf-status {
        margin-top: 10px;
        padding: 8px 10px;
        border-radius: 6px;
        font-size: 12px;
        display: none;
      }

      .bf-status.success {
        display: block;
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
      }

      .bf-status.error {
        display: block;
        background-color: #f8d7da;
        color: #842029;
        border: 1px solid #f5c2c7;
      }
    </style>

    <div class="bf-modal" id="modal">
      <div class="bf-header">
        <div class="bf-title">
          <span>💬</span> Send Feedback
        </div>
        <button class="bf-close" id="close-btn" aria-label="Close" type="button">&times;</button>
      </div>

      <div class="bf-form-group">
        <label class="bf-label">Application</label>
        <div class="bf-app-badge" id="app-badge">App</div>
      </div>

      <form id="feedback-form">
        <div class="bf-form-group">
          <label class="bf-label" for="user-name">Your Name</label>
          <input
            type="text"
            id="user-name"
            class="bf-input"
            placeholder="e.g. Maria / Luca"
            required
            maxlength="100"
          />
        </div>

        <div class="bf-form-group">
          <label class="bf-label" for="user-message">Suggestions / Problems</label>
          <textarea
            id="user-message"
            class="bf-textarea"
            placeholder="What is working well, what is broken, or what would you like improved?"
            required
            maxlength="4000"
          ></textarea>
        </div>

        <button type="submit" class="bf-submit" id="submit-btn">
          Send to Slack
        </button>
      </form>

      <div class="bf-status" id="status-msg"></div>
    </div>

    <button class="bf-trigger" id="trigger-btn" type="button" aria-expanded="false">
      <svg class="bf-icon" viewBox="0 0 16 16">
        <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5.414L2.707 14.707A1 1 0 0 1 1 14V2zm2-1a1 1 0 0 0-1 1v11.293l2.293-2.293A1 1 0 0 1 4.707 11H12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H4z"/>
      </svg>
      <span>Feedback</span>
    </button>
  `;

  class BiocoreFeedback extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this.shadowRoot.appendChild(template.content.cloneNode(true));

      this._modal = this.shadowRoot.getElementById("modal");
      this._triggerBtn = this.shadowRoot.getElementById("trigger-btn");
      this._closeBtn = this.shadowRoot.getElementById("close-btn");
      this._form = this.shadowRoot.getElementById("feedback-form");
      this._nameInput = this.shadowRoot.getElementById("user-name");
      this._messageInput = this.shadowRoot.getElementById("user-message");
      this._submitBtn = this.shadowRoot.getElementById("submit-btn");
      this._statusMsg = this.shadowRoot.getElementById("status-msg");
      this._appBadge = this.shadowRoot.getElementById("app-badge");
    }

    connectedCallback() {
      const appName = this.getAttribute("app-name") || document.title || "Web App";
      this._appBadge.textContent = appName;

      // Restore saved name from localStorage if available
      try {
        const savedName = localStorage.getItem("biocore_feedback_user_name");
        if (savedName) {
          this._nameInput.value = savedName;
        }
      } catch (e) {
        // LocalStorage not permitted in some contexts
      }

      this._triggerBtn.addEventListener("click", () => this.toggleModal());
      this._closeBtn.addEventListener("click", () => this.closeModal());
      this._form.addEventListener("submit", (e) => this.handleSubmit(e));

      // Close on escape key
      this._escapeHandler = (e) => {
        if (e.key === "Escape" && this._modal.classList.contains("open")) {
          this.closeModal();
        }
      };
      document.addEventListener("keydown", this._escapeHandler);
    }

    disconnectedCallback() {
      document.removeEventListener("keydown", this._escapeHandler);
    }

    toggleModal() {
      const isOpen = this._modal.classList.contains("open");
      if (isOpen) {
        this.closeModal();
      } else {
        this.openModal();
      }
    }

    openModal() {
      this._modal.classList.add("open");
      this._triggerBtn.setAttribute("aria-expanded", "true");
      this._statusMsg.className = "bf-status";
      this._statusMsg.textContent = "";
      setTimeout(() => {
        if (!this._nameInput.value.trim()) {
          this._nameInput.focus();
        } else {
          this._messageInput.focus();
        }
      }, 50);
    }

    closeModal() {
      this._modal.classList.remove("open");
      this._triggerBtn.setAttribute("aria-expanded", "false");
    }

    async handleSubmit(event) {
      event.preventDefault();
      const name = this._nameInput.value.trim();
      const message = this._messageInput.value.trim();
      const appName = this.getAttribute("app-name") || document.title || "Web App";
      const apiUrl = this.getAttribute("api-url") || defaultApiUrl || "/api/feedback";

      if (!name || !message) {
        return;
      }

      // Save name for convenience next time
      try {
        localStorage.setItem("biocore_feedback_user_name", name);
      } catch (e) {}

      this._submitBtn.disabled = true;
      this._submitBtn.textContent = "Sending...";
      this._statusMsg.className = "bf-status";
      this._statusMsg.textContent = "";

      const payload = {
        name: name,
        app: appName,
        message: message,
        page_url: window.location.href,
      };

      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
          this._statusMsg.className = "bf-status success";
          this._statusMsg.textContent = "Message sent to Slack. Thank you!";
          this._messageInput.value = "";
          setTimeout(() => {
            this.closeModal();
            this._statusMsg.className = "bf-status";
          }, 2500);
        } else {
          const errorDetail = data.detail || "Error sending feedback. Please try again.";
          this._statusMsg.className = "bf-status error";
          this._statusMsg.textContent = errorDetail;
        }
      } catch (err) {
        this._statusMsg.className = "bf-status error";
        this._statusMsg.textContent = "Network error: could not connect to feedback server.";
      } finally {
        this._submitBtn.disabled = false;
        this._submitBtn.textContent = "Send to Slack";
      }
    }
  }

  // Register Custom Element
  if (!customElements.get("biocore-feedback")) {
    customElements.define("biocore-feedback", BiocoreFeedback);
  }
})();
