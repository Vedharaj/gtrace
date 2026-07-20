export function renderStatusBar(container, state, onToggleTerminal) {
  container.innerHTML = `
    <div class="statusbar">
      <div class="statusbar-left">
        <div class="status-item" id="btn-show-logs">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
          <span>LOGS: READY</span>
        </div>
        <div class="status-item" id="btn-show-terminal">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
          <span>&lt;&gt; TERMINAL: SESSION ACTIVE</span>
        </div>
      </div>

      <div class="statusbar-right">
        <span>TRACE BUFFER: 1.2GB LOADED</span>
      </div>
    </div>
  `;

  container.querySelector('#btn-show-logs').addEventListener('click', onToggleTerminal);
  container.querySelector('#btn-show-terminal').addEventListener('click', onToggleTerminal);
}
