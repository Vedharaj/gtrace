export function renderInstructionCommit(container, state) {
  const formatNum = (num) => num ? num.toLocaleString() : '0';
  const scrubberPosPct = state.scrubberPosPct || 76;

  container.innerHTML = `
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Instruction Commit</span>
      </div>

      <div class="commit-bars">
        <div class="commit-group">
          <div class="commit-label-row">
            <span class="stat-label">INSTRUCTIONS</span>
            <span class="commit-val mono" style="color: var(--color-blue);">${formatNum(state.committedInsts)}</span>
          </div>
          <div class="commit-bar-bg">
            <div class="commit-bar-fill fill-blue" style="width: ${scrubberPosPct}%;"></div>
          </div>
        </div>

        <div class="commit-group">
          <div class="commit-label-row">
            <span class="stat-label">MICRO-OPS</span>
            <span class="commit-val mono" style="color: var(--color-purple);">${formatNum(state.committedOps)}</span>
          </div>
          <div class="commit-bar-bg">
            <div class="commit-bar-fill fill-purple" style="width: ${scrubberPosPct}%;"></div>
          </div>
        </div>
      </div>

      <div class="commit-footer">
        <span>Retire Rate: ${state.retireRate || '1.48'} uops/inst</span>
        <span>Flush Rate: ${state.flushRate || '0.04'}%</span>
      </div>
    </div>
  `;
}
