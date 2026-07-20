export function renderExecutionTimeline(container, state, onScrub) {
  const scrubberPosPct = state.scrubberPosPct || 76;
  const maxVal = state.maxCycles || 4102931;

  const formatCyclesCompact = (val) => {
    if (!val) return '0';
    if (val >= 1000000) return (val / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    if (val >= 1000) return (val / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    return val.toString();
  };

  const axis0 = 0;
  const axis1 = formatCyclesCompact(Math.round(maxVal * 0.25));
  const axis2 = formatCyclesCompact(Math.round(maxVal * 0.5));
  const axis3 = formatCyclesCompact(Math.round(maxVal * 0.75));
  const axis4 = formatCyclesCompact(maxVal);

  container.innerHTML = `
    <div class="timeline-panel">
      <div class="timeline-header">
        <span class="panel-title">Execution Timeline</span>
        <div class="legend">
          <div class="legend-item">
            <span class="legend-dot dot-commits"></span>
            <span>COMMITS</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot dot-misses"></span>
            <span>CACHE MISSES</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot dot-branches"></span>
            <span>BRANCHES</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot dot-stalls"></span>
            <span>PIPELINE STALLS</span>
          </div>
        </div>
      </div>

      <div class="timeline-canvas-container" id="timeline-container">
        <!-- Green Vertical Scrubber Line -->
        <div class="scrubber-line" id="scrubber-line" style="left: calc(100px + (100% - 100px) * ${scrubberPosPct / 100});">
          <div class="scrubber-head"></div>
        </div>

        <div class="timeline-axis">
          <span>${axis0}</span>
          <span>${axis1}</span>
          <span>${axis2}</span>
          <span>${axis3}</span>
          <span>${axis4}</span>
        </div>

        <div class="timeline-track-list">
          <!-- Track 1: COMMITS (Green Blocks) -->
          <div class="timeline-track">
            <span class="track-label">COMMITS</span>
            <div class="track-content">
              <div style="position: absolute; left: 10%; width: 12%; height: 100%; background: rgba(46, 125, 50, 0.25); border-radius: 2px;"></div>
              <div style="position: absolute; left: 23%; width: 15%; height: 100%; background: rgba(46, 125, 50, 0.45); border-radius: 2px;"></div>
              <div style="position: absolute; left: 40%; width: 8%; height: 100%; background: rgba(46, 125, 50, 0.35); border-radius: 2px;"></div>
              <div style="position: absolute; left: 49%; width: 6%; height: 100%; background: rgba(46, 125, 50, 0.5); border-radius: 2px;"></div>
              <div style="position: absolute; left: 60%; width: 14%; height: 100%; background: rgba(46, 125, 50, 0.4); border-radius: 2px;"></div>
              <div style="position: absolute; left: 76%; width: 11%; height: 100%; background: rgba(46, 125, 50, 0.5); border-radius: 2px;"></div>
              <div style="position: absolute; left: 91%; width: 7%; height: 100%; background: rgba(46, 125, 50, 0.3); border-radius: 2px;"></div>
            </div>
          </div>

          <!-- Track 2: CACHE (Red Dots) -->
          <div class="timeline-track">
            <span class="track-label">CACHE</span>
            <div class="track-content" style="display: flex; align-items: center;">
              <div style="position: absolute; left: 22%; width: 8px; height: 8px; background-color: var(--color-red); border-radius: 50%;"></div>
              <div style="position: absolute; left: 25%; width: 8px; height: 8px; background-color: var(--color-red); border-radius: 50%;"></div>
              <div style="position: absolute; left: 52%; width: 8px; height: 8px; background-color: var(--color-red); border-radius: 50%;"></div>
              <div style="position: absolute; left: 82%; width: 8px; height: 8px; background-color: var(--color-red); border-radius: 50%;"></div>
              <div style="position: absolute; left: 86%; width: 8px; height: 8px; background-color: var(--color-red); border-radius: 50%;"></div>
            </div>
          </div>

          <!-- Track 3: BRANCHES (Purple Ticks) -->
          <div class="timeline-track">
            <span class="track-label">BRANCHES</span>
            <div class="track-content" style="display: flex; align-items: center;">
              <div style="position: absolute; left: 15%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 28%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 35%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 51%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 66%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 73%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
              <div style="position: absolute; left: 94%; width: 3px; height: 18px; background-color: var(--color-purple); border-radius: 1px;"></div>
            </div>
          </div>

          <!-- Track 4: PIPELINE STALLS (Amber Blocks) -->
          <div class="timeline-track">
            <span class="track-label">STALLS</span>
            <div class="track-content">
              <div style="position: absolute; left: 13%; width: 3%; height: 100%; background: rgba(249, 168, 37, 0.35); border-radius: 2px;"></div>
              <div style="position: absolute; left: 18%; width: 7%; height: 100%; background: rgba(249, 168, 37, 0.45); border-radius: 2px;"></div>
              <div style="position: absolute; left: 26%; width: 4%; height: 100%; background: rgba(249, 168, 37, 0.35); border-radius: 2px;"></div>
              <div style="position: absolute; left: 37%; width: 5%; height: 100%; background: rgba(249, 168, 37, 0.5); border-radius: 2px;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  // Interactivity for Scrubber Dragging / Clicking
  const timelineElem = container.querySelector('#timeline-container');
  let isDragging = false;

  const updateScrubber = (e) => {
    const rect = timelineElem.getBoundingClientRect();
    const trackStart = rect.left + 100;
    const trackWidth = rect.width - 100;
    let clickX = e.clientX - trackStart;
    clickX = Math.max(0, Math.min(clickX, trackWidth));
    const pct = (clickX / trackWidth) * 100;
    onScrub(pct);
  };

  timelineElem.addEventListener('mousedown', (e) => {
    isDragging = true;
    updateScrubber(e);
  });

  window.addEventListener('mousemove', (e) => {
    if (isDragging) updateScrubber(e);
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });
}
