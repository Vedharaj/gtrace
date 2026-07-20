export function renderCpuActivity(container, state) {
  const busyPct = state.busyPct || 84;
  const idlePct = 100 - busyPct;

  const formatCycles = (cycles) => {
    if (!cycles) return '0';
    if (cycles >= 1e6) return (cycles / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (cycles >= 1e3) return (cycles / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
    return cycles.toLocaleString();
  };

  const maxCyclesLabel = formatCycles(state.maxCycles || 4102931);

  container.innerHTML = `
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">CPU Activity</span>
        <span class="panel-subtitle">Core-0 Affinity</span>
      </div>

      <div class="activity-bar-wrapper">
        <div class="stacked-bar">
          <div class="bar-segment segment-busy" style="width: ${busyPct}%;">
            BUSY ${busyPct}%
          </div>
          <div class="bar-segment segment-idle" style="width: ${idlePct}%;">
            IDLE ${idlePct}%
          </div>
        </div>
        <div class="activity-ticks">
          <span>0 cycles</span>
          <span>${maxCyclesLabel} cycles</span>
        </div>
      </div>

      <div class="activity-stats">
        <div class="stat-item">
          <span class="stat-label">USER</span>
          <span class="stat-val">${state.userPct || '78.2'}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">KERNEL</span>
          <span class="stat-val">${state.kernelPct || '5.8'}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">WAIT</span>
          <span class="stat-val">${state.waitPct || '1.2'}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">INTERRUPTS</span>
          <span class="stat-val">${state.interruptsPct || '0.8'}%</span>
        </div>
      </div>
    </div>
  `;
}
