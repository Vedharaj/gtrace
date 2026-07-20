export function renderMetricsOverview(container, state) {
  const formatNum = (num) => num.toLocaleString();

  container.innerHTML = `
    <div class="metrics-row">
      <!-- Card 1: Cycles -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">CYCLES</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-cycles">${formatNum(state.cycles)}</span>
          <svg class="metric-chart" viewBox="0 0 50 20">
            <path d="M 0,15 Q 10,5 20,12 T 40,8 T 50,14" fill="none" stroke="#94A3B8" stroke-width="1.5" />
          </svg>
        </div>
      </div>

      <!-- Card 2: Committed Insts -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">COMMITTED INSTS</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-insts">${formatNum(state.committedInsts)}</span>
        </div>
      </div>

      <!-- Card 3: Committed Ops -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">COMMITTED OPS</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-ops">${formatNum(state.committedOps)}</span>
        </div>
      </div>

      <!-- Card 4: IPC -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">IPC</span>
          <span class="metric-badge badge-target">TARGET: 0.8</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-ipc">${state.ipc.toFixed(2)}</span>
        </div>
        <div class="metric-bar-container">
          <div class="metric-bar-fill" style="width: ${(state.ipc / 0.8) * 100}%; background-color: var(--green-primary);"></div>
        </div>
      </div>

      <!-- Card 5: CPI -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">CPI</span>
          <span class="metric-badge badge-warning">LOWER IS BETTER</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-cpi">${state.cpi.toFixed(2)}</span>
        </div>
        <div class="metric-bar-container">
          <div class="metric-bar-fill" style="width: 70%; background-color: var(--color-amber);"></div>
        </div>
      </div>

      <!-- Card 6: Execution Time -->
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">EXECUTION TIME</span>
        </div>
        <div class="metric-body">
          <span class="metric-value val-time">${state.execTime.toFixed(2)}<span class="metric-unit">s</span></span>
        </div>
      </div>
    </div>
  `;
}
