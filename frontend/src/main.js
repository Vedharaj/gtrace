import { renderSidebar } from './components/Sidebar.js';
import { renderHeader } from './components/Header.js';
import { renderPlaybackToolbar } from './components/PlaybackToolbar.js';
import { renderMetricsOverview } from './components/MetricsOverview.js';
import { renderSimulationEnvironment } from './components/SimulationEnvironment.js';
import { renderCpuActivity } from './components/CpuActivity.js';
import { renderInstructionCommit } from './components/InstructionCommit.js';
import { renderExecutionTimeline } from './components/ExecutionTimeline.js';
import {
  renderEditorView,
  renderDatapathView,
  renderMemoryView,
  renderCacheView,
  renderRegistersView,
  renderPipelineView,
  renderBranchView,
  renderStatisticsView,
  renderSettingsView,
  renderHelpView
} from './components/Views.js';
import { renderStatusBar } from './components/StatusBar.js';

// Application State
const state = {
  activeView: 'dashboard',
  isSidebarCollapsed: false,
  loadedFile: 'vmlinux_boot.trace',
  maxCycles: 4102931,
  cycles: 3102931,
  committedInsts: 2200000,
  committedOps: 2600000,
  ipc: 0.71,
  cpi: 1.42,
  execTime: 2.13,
  busyPct: 84,
  userPct: 78.2,
  kernelPct: 5.8,
  waitPct: 1.2,
  interruptsPct: 0.8,
  retireRate: 1.48,
  flushRate: 0.04,
  scrubberPosPct: 76,
  isLogOpen: false,
  isPlaying: false,
  playbackTimer: null,
  speedMs: 500
};

// gem5 Trace Stream Mock Records
const rawTraceLogs = [
  "  77000: system.cpu: T0 : 0x102a4 @_start    : jal ra, 44                 : IntAlu :  D=0x00000000000102a8",
  " 126000: system.cpu: T0 : 0x102d0 @_start+44    : auipc gp, 108              : IntAlu :  D=0x000000000007c2d0",
  " 175000: system.cpu: T0 : 0x102d4 @_start+48    : addi gp, gp, -480          : IntAlu :  D=0x000000000007c0f0",
  " 224000: system.cpu: T0 : 0x102d8 @_start+52    : c_jr ra                    : IntAlu :",
  " 273000: system.cpu: T0 : 0x102a8 @_start+4    : c_mv a5, a0                : IntAlu :  D=0x0000000000000000",
  " 371000: system.cpu: T0 : 0x102aa @_start+6    : auipc a0, 0                : IntAlu :  D=0x00000000000102aa",
  " 469000: system.cpu: T0 : 0x102ae @_start+10    : addi a0, a0, 232           : IntAlu :  D=0x0000000000010392",
  " 518000: system.cpu: T0 : 0x102b2 @_start+14    : c_ldsp a1, 0(sp)           : MemRead :  D=0x0000000000000001 A=0x7fffffffffffff20",
  " 630000: system.cpu: T0 : 0x102b4 @_start+16    : c_addi4spn a2, sp, 8       : IntAlu :  D=0x7fffffffffffff28",
  " 728000: system.cpu: T0 : 0x102b6 @_start+18    : andi sp, sp, -16           : IntAlu :  D=0x7fffffffffffff20",
  " 826000: system.cpu: T0 : 0x102ba @_start+22    : auipc a3, 0                : IntAlu :  D=0x00000000000102ba",
  " 938000: system.cpu: T0 : 0x102be @_start+26    : addi a3, a3, 1504          : IntAlu :  D=0x000000000001089a",
  "1036000: system.cpu: T0 : 0x102c2 @_start+30    : auipc a4, 0                : IntAlu :  D=0x00000000000102c2",
  "1134000: system.cpu: T0 : 0x102c6 @_start+34    : addi a4, a4, 1640          : IntAlu :  D=0x000000000001092a",
  "1183000: system.cpu: T0 : 0x102ca @_start+38    : c_mv a6, sp                : IntAlu :  D=0x7fffffffffffff20",
  "1232000: system.cpu: T0 : 0x102cc @_start+40    : jal zero, 230              : IntAlu :  D=0x00000000000102d0",
  "1281000: system.cpu: T0 : 0x103b2 @__libc_start_main : c_addi16sp sp, -320   : IntAlu :  D=0x7ffffffffffffde0",
  "1330000: system.cpu: T0 : 0x103b4 @__libc_start_main+2 : lui a7, 0           : IntAlu :  D=0x0000000000000000",
  "1379000: system.cpu: T0 : 0x103b8 @__libc_start_main+6 : c_sdsp s0, 304(sp)  : MemWrite : D=0x0000000000000000 A=0x7fffffffffffff10",
  "1449000: system.cpu: T0 : 0x103ba @__libc_start_main+8 : c_sdsp s1, 296(sp)  : MemWrite : D=0x0000000000000000 A=0x7fffffffffffff08",
  "2100000: system.cpu: T0 : 0x10400 @coremark_main+12 : addi s0, sp, 320      : IntAlu :  D=0x7fffffffffffff20",
  "2540000: system.cpu: T0 : 0x10420 @matrix_mul+4    : fld ft0, 0(a0)          : MemRead :  D=0x400921fb54442d18 A=0x10048",
  "3102931: system.cpu: T0 : 0x104a0 @crc_calc+32     : xor a0, a0, a1          : IntAlu :  D=0x000000000000004f"
];

function initApp() {
  const statusbarElem = document.getElementById('main-statusbar');
  renderStatusBar(statusbarElem, state, toggleLogModal);
  renderApp();
  setupModalEvents();
  setupKeyboardShortcuts();
}

function updateCycleState(pct) {
  state.scrubberPosPct = Math.max(0, Math.min(100, pct));
  state.cycles = Math.round((state.scrubberPosPct / 100) * state.maxCycles);
  state.committedInsts = Math.round((state.scrubberPosPct / 100) * 2913004);
  state.committedOps = Math.round((state.scrubberPosPct / 100) * 3450112);
  state.execTime = (state.cycles / 2000000000) * 1000;
  state.ipc = Number((0.65 + (state.scrubberPosPct / 100) * 0.1).toFixed(2));
  state.cpi = Number((1 / state.ipc).toFixed(2));
  renderApp();
}

function togglePlay() {
  state.isPlaying = !state.isPlaying;

  if (state.isPlaying) {
    state.playbackTimer = setInterval(() => {
      let nextPct = state.scrubberPosPct + 1;
      if (nextPct > 100) {
        nextPct = 0;
      }
      updateCycleState(nextPct);
    }, state.speedMs);
  } else {
    if (state.playbackTimer) {
      clearInterval(state.playbackTimer);
      state.playbackTimer = null;
    }
  }

  renderApp();
}

function handleFileSelect(fileName, fileObj) {
  state.loadedFile = fileName;

  if (fileObj) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split('\n').filter(line => line.trim().length > 0);
      if (lines.length > 0) {
        document.getElementById('terminal-output').textContent = lines.slice(0, 500).join('\n');
      }
    };
    reader.readAsText(fileObj);
  }

  renderApp();
}

function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    if (e.code === 'Space') {
      e.preventDefault();
      togglePlay();
    } else if (e.code === 'ArrowLeft') {
      e.preventDefault();
      updateCycleState(state.scrubberPosPct - 1);
    } else if (e.code === 'ArrowRight') {
      e.preventDefault();
      updateCycleState(state.scrubberPosPct + 1);
    } else if (e.code === 'Home') {
      e.preventDefault();
      updateCycleState(0);
    } else if (e.code === 'End') {
      e.preventDefault();
      updateCycleState(100);
    } else if (e.code === 'KeyR') {
      e.preventDefault();
      if (state.isPlaying) togglePlay();
      updateCycleState(0);
    }
  });
}

const playbackActions = {
  onTogglePlay: () => togglePlay(),
  onStepPrev: () => updateCycleState(state.scrubberPosPct - 1),
  onStepNext: () => updateCycleState(state.scrubberPosPct + 1),
  onJumpStart: () => updateCycleState(0),
  onJumpEnd: () => updateCycleState(100),
  onReset: () => {
    if (state.isPlaying) togglePlay();
    updateCycleState(0);
  },
  onChangeSpeed: (newSpeedMs) => {
    state.speedMs = newSpeedMs;
    if (state.isPlaying) {
      togglePlay();
      togglePlay();
    } else {
      renderApp();
    }
  }
};

function renderApp() {
  const sidebarElem = document.getElementById('sidebar');
  const headerElem = document.getElementById('main-header');
  const viewElem = document.getElementById('view-content');

  // Render Left Navigation Sidebar
  renderSidebar(
    sidebarElem,
    state.activeView,
    state.isSidebarCollapsed,
    (viewId) => {
      state.activeView = viewId;
      renderApp();
    },
    () => {
      state.isSidebarCollapsed = !state.isSidebarCollapsed;
      renderApp();
    }
  );

  // Render Header with Breadcrumb
  renderHeader(headerElem, state.activeView, state, handleFileSelect);

  viewElem.innerHTML = '';

  if (state.activeView === 'dashboard') {
    // 1. Trace Summary KPI Cards
    const metricsContainer = document.createElement('div');
    renderMetricsOverview(metricsContainer, state);
    viewElem.appendChild(metricsContainer.firstElementChild);

    // 2. Simulation Environment Section
    const simEnvContainer = document.createElement('div');
    renderSimulationEnvironment(simEnvContainer, state);
    viewElem.appendChild(simEnvContainer.firstElementChild);

    // 3. CPU Activity & Instruction Commit
    const middleRow = document.createElement('div');
    middleRow.className = 'middle-row';
    
    const cpuContainer = document.createElement('div');
    renderCpuActivity(cpuContainer, state);
    middleRow.appendChild(cpuContainer.firstElementChild);

    const commitContainer = document.createElement('div');
    renderInstructionCommit(commitContainer, state);
    middleRow.appendChild(commitContainer.firstElementChild);

    viewElem.appendChild(middleRow);

    // 4. Execution Timeline
    const timelineContainer = document.createElement('div');
    renderExecutionTimeline(timelineContainer, state, (newPct) => {
      updateCycleState(newPct);
    });
    viewElem.appendChild(timelineContainer.firstElementChild);

  } else if (state.activeView === 'datapath' || state.activeView === 'pipeline') {
    // 1. Appends Global Playback Toolbar at the top center
    const tbContainer = document.createElement('div');
    renderPlaybackToolbar(tbContainer, state, playbackActions);
    viewElem.appendChild(tbContainer.firstElementChild);

    // 2. Appends Datapath Content Panel
    const datapathCard = document.createElement('div');
    renderDatapathView(datapathCard, state);
    viewElem.appendChild(datapathCard.firstElementChild);

  } else if (state.activeView === 'editor') {
    renderEditorView(viewElem, state);
  } else if (state.activeView === 'memory') {
    renderMemoryView(viewElem, state);
  } else if (state.activeView === 'cache') {
    renderCacheView(viewElem, state);
  } else if (state.activeView === 'registers') {
    renderRegistersView(viewElem, state);
  } else if (state.activeView === 'branch') {
    renderBranchView(viewElem, state);
  } else if (state.activeView === 'statistics') {
    renderStatisticsView(viewElem, state);
  } else if (state.activeView === 'settings') {
    renderSettingsView(viewElem, state);
  } else if (state.activeView === 'help') {
    renderHelpView(viewElem, state);
  }

  const toggleBtn = document.getElementById('terminal-toggle-btn');
  if (toggleBtn) {
    toggleBtn.onclick = toggleLogModal;
  }
}

function toggleLogModal() {
  const modal = document.getElementById('log-modal');
  state.isLogOpen = !state.isLogOpen;
  if (state.isLogOpen) {
    modal.classList.remove('hidden');
    populateTerminalLogs();
  } else {
    modal.classList.add('hidden');
  }
}

function populateTerminalLogs() {
  const outputElem = document.getElementById('terminal-output');
  if (!outputElem.textContent || outputElem.textContent === 'Terminal output cleared.') {
    outputElem.textContent = rawTraceLogs.join('\n');
  }
}

function setupModalEvents() {
  const modal = document.getElementById('log-modal');
  const overlay = document.getElementById('modal-overlay');
  const closeBtn = document.getElementById('modal-close-btn');
  const clearBtn = document.getElementById('modal-clear-btn');

  overlay.addEventListener('click', toggleLogModal);
  closeBtn.addEventListener('click', toggleLogModal);
  clearBtn.addEventListener('click', () => {
    document.getElementById('terminal-output').textContent = 'Terminal output cleared.';
  });
}

document.addEventListener('DOMContentLoaded', initApp);
