export function renderSimulationEnvironment(container, state) {
  const formatNum = (num) => num.toLocaleString();

  const simSecs = (state.execTime || 2.05).toFixed(2);
  const hostSecs = ((state.execTime || 2.05) * 6.9).toFixed(1);
  const finalTickVal = formatNum((state.cycles || 4102931) * 1000);
  const tickRateVal = ((state.ipc || 0.71) * 2.05).toFixed(2);
  const memUsedGB = 3.2;
  const memTotalGB = 16.0;
  const memPct = Math.round((memUsedGB / memTotalGB) * 100);

  container.innerHTML = `
    <div class="sim-env-panel">
      <div class="sim-env-header">
        <div>
          <h3 class="sim-env-title">Simulation Environment</h3>
          <span class="sim-env-subtitle">Host Performance During Simulation</span>
        </div>
        <div class="sim-env-badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          <span>gem5 Host Engine Active</span>
        </div>
      </div>

      <div class="sim-grid">
        <!-- Panel 1: Simulation Timing -->
        <div class="sim-card">
          <div class="sim-card-header">
            <span class="sim-card-title">Simulation Timing</span>
          </div>

          <div class="sim-metrics-grid">
            <!-- simSeconds -->
            <div class="sim-metric-item" title="Time represented inside the simulated machine">
              <div class="sim-metric-top">
                <span class="sim-label">Simulation Time</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="icon-green"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              </div>
              <div class="sim-val-group">
                <span class="sim-val val-green">${simSecs}</span>
                <span class="sim-unit">s</span>
              </div>
              <span class="sim-desc">Simulated machine duration</span>
            </div>

            <!-- hostSeconds -->
            <div class="sim-metric-item" title="Real execution time on host computer">
              <div class="sim-metric-top">
                <span class="sim-label">Host Execution Time</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="icon-gray"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              </div>
              <div class="sim-val-group">
                <span class="sim-val val-gray">${hostSecs}</span>
                <span class="sim-unit">s</span>
              </div>
              <span class="sim-desc">Host wall-clock runtime</span>
            </div>

            <!-- finalTick -->
            <div class="sim-metric-item" title="Final tick index of current simulation">
              <div class="sim-metric-top">
                <span class="sim-label">Final Tick</span>
                <span class="sim-val-sm mono">${finalTickVal}</span>
              </div>
              <div class="mini-timeline-container">
                <div class="mini-timeline-track">
                  <div class="mini-timeline-fill" style="width: ${(state.scrubberPosPct || 76)}%;"></div>
                  <div class="mini-timeline-endpoint" style="left: ${(state.scrubberPosPct || 76)}%;"></div>
                </div>
              </div>
              <span class="sim-desc">Simulation end tick marker</span>
            </div>

            <!-- simTicks -->
            <div class="sim-metric-item" title="Simulation ticks progression">
              <div class="sim-metric-top">
                <span class="sim-label">Simulation Ticks</span>
                <span class="sim-val-sm mono">${formatNum(state.cycles)}</span>
              </div>
              <div class="mini-chart-container">
                <svg class="mini-sparkline-svg" viewBox="0 0 100 24">
                  <path d="M 0,22 L 20,18 L 40,12 L 60,15 L 80,6 L 100,2" fill="none" stroke="var(--green-primary)" stroke-width="2" stroke-linecap="round" />
                </svg>
              </div>
              <span class="sim-desc">Tick progression rate</span>
            </div>
          </div>
        </div>

        <!-- Panel 2: Simulation Resources -->
        <div class="sim-card">
          <div class="sim-card-header">
            <span class="sim-card-title">Simulation Resources</span>
          </div>

          <div class="sim-metrics-grid">
            <!-- hostTickRate -->
            <div class="sim-metric-item" title="Simulation speed in ticks per second">
              <div class="sim-metric-top">
                <span class="sim-label">Simulation Speed</span>
                <span class="sim-val-sm mono" style="color: var(--green-primary);">${tickRateVal} GTicks/s</span>
              </div>
              <div class="perf-bar-wrapper">
                <div class="perf-bar-bg">
                  <div class="perf-bar-fill" style="width: 72%;"></div>
                  <div class="perf-target-marker" style="left: 80%;" title="Target: 2.00 GTicks/s"></div>
                </div>
              </div>
              <div class="sim-sub-row">
                <span class="sim-desc">Host performance throughput</span>
                <span class="sim-target-label">Target: 2.0 GTicks/s</span>
              </div>
            </div>

            <!-- hostMemory -->
            <div class="sim-metric-item" title="Host system memory utilization">
              <div class="sim-metric-top">
                <span class="sim-label">Host Memory</span>
                <span class="sim-val-sm mono">${memUsedGB} GB / ${memTotalGB} GB (${memPct}%)</span>
              </div>
              <div class="mem-bar-wrapper">
                <div class="mem-bar-bg">
                  <div class="mem-bar-fill" style="width: ${memPct}%;"></div>
                </div>
              </div>
              <span class="sim-desc">RAM allocated by gem5 process</span>
            </div>

            <!-- simInsts -->
            <div class="sim-metric-item" title="Total instructions executed by simulator">
              <div class="sim-metric-top">
                <span class="sim-label">Executed Instructions</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="icon-blue"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
              </div>
              <div class="sim-val-group">
                <span class="sim-val val-blue">${formatNum(state.committedInsts)}</span>
              </div>
              <div class="mini-chart-container" style="height: 14px; margin-top: 4px;">
                <svg class="mini-sparkline-svg" viewBox="0 0 100 14">
                  <path d="M 0,12 L 25,9 L 50,6 L 75,4 L 100,2" fill="none" stroke="var(--color-blue)" stroke-width="1.5" />
                </svg>
              </div>
            </div>

            <!-- simOps -->
            <div class="sim-metric-item" title="Total micro-operations executed by simulator">
              <div class="sim-metric-top">
                <span class="sim-label">Executed Micro Operations</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="icon-purple"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
              </div>
              <div class="sim-val-group">
                <span class="sim-val val-purple">${formatNum(state.committedOps)}</span>
              </div>
              <div class="mini-chart-container" style="height: 14px; margin-top: 4px;">
                <svg class="mini-sparkline-svg" viewBox="0 0 100 14">
                  <path d="M 0,12 L 20,10 L 45,7 L 70,3 L 100,1" fill="none" stroke="var(--color-purple)" stroke-width="1.5" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
