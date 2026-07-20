export function renderPlaybackToolbar(container, state, actions) {
  const formatNum = (num) => num.toLocaleString();

  const isPlaying = state.isPlaying || false;
  const currentCycle = state.cycles || 0;
  const maxCycles = state.maxCycles || 4102931;
  const speedMs = state.speedMs || 500;

  container.innerHTML = `
    <div class="playback-toolbar-container">
      <div class="playback-toolbar">
        <!-- Replay Control Buttons -->
        <div class="playback-controls">
          <!-- Jump to Start -->
          <button class="tb-btn" id="btn-jump-start" title="Jump to Start (Home)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line></svg>
          </button>

          <!-- Step Back -->
          <button class="tb-btn" id="btn-step-prev" title="Previous Step (Left Arrow)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="19 20 9 12 19 4 19 20"></polygon></svg>
          </button>

          <!-- Play / Pause -->
          <button class="tb-btn btn-play ${isPlaying ? 'playing' : ''}" id="btn-play-pause" title="${isPlaying ? 'Pause (Space)' : 'Play Execution (Space)'}">
            ${isPlaying ? `
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
            ` : `
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            `}
          </button>

          <!-- Step Forward -->
          <button class="tb-btn" id="btn-step-next" title="Next Step (Right Arrow)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="5 4 15 12 5 20 5 4"></polygon></svg>
          </button>

          <!-- Jump to End -->
          <button class="tb-btn" id="btn-jump-end" title="Jump to End (End)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line></svg>
          </button>

          <div class="tb-divider"></div>

          <!-- Reset -->
          <button class="tb-btn" id="btn-reset" title="Reset Replay (R)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path></svg>
          </button>
        </div>

        <div class="tb-divider"></div>

        <!-- Playback Speed Control -->
        <div class="playback-speed">
          <span class="speed-label">Playback Speed</span>
          <input type="range" id="speed-slider" min="100" max="2000" step="100" value="${speedMs}" class="speed-input" />
          <span class="speed-val mono">${speedMs} ms</span>
        </div>

        <div class="tb-divider"></div>

        <!-- Cycle Counter Badge -->
        <div class="cycle-badge ${isPlaying ? 'active-replay' : ''}">
          <span class="cycle-title">CYCLE</span>
          <span class="cycle-num mono">${formatNum(currentCycle)} / ${formatNum(maxCycles)}</span>
        </div>
      </div>
    </div>
  `;

  // Attach button click handlers
  container.querySelector('#btn-jump-start').onclick = actions.onJumpStart;
  container.querySelector('#btn-step-prev').onclick = actions.onStepPrev;
  container.querySelector('#btn-play-pause').onclick = actions.onTogglePlay;
  container.querySelector('#btn-step-next').onclick = actions.onStepNext;
  container.querySelector('#btn-jump-end').onclick = actions.onJumpEnd;
  container.querySelector('#btn-reset').onclick = actions.onReset;

  const slider = container.querySelector('#speed-slider');
  slider.oninput = (e) => {
    actions.onChangeSpeed(Number(e.target.value));
  };
}
