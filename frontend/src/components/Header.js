export function renderHeader(container, activeView, state, onFileSelect) {
  const currentFileName = state?.loadedFile || 'vmlinux_boot.trace';

  const viewTitles = {
    dashboard: 'Dashboard',
    editor: 'Editor',
    datapath: 'Datapath',
    memory: 'Memory',
    cache: 'Cache',
    registers: 'Registers',
    pipeline: 'Pipeline',
    branch: 'Branch Predictor',
    statistics: 'Statistics',
    settings: 'Settings',
    help: 'Help'
  };

  const pageTitle = viewTitles[activeView] || 'Dashboard';

  container.innerHTML = `
    <div class="header">
      <div class="header-left">
        <!-- Breadcrumb Navigation -->
        <div class="breadcrumb">
          <span class="crumb-root">GTrace</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
          <span class="crumb-current">${pageTitle}</span>
        </div>

        <div class="brand-divider"></div>

        <!-- TOP LEFT FILE & FOLDER IMPORT PANEL -->
        <div class="file-import-panel-wrapper">
          <button id="import-btn" class="import-panel-btn" title="Open Trace File or Folder from System">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              <line x1="12" y1="11" x2="12" y2="17"></line>
              <line x1="9" y1="14" x2="15" y2="14"></line>
            </svg>
            <span>Open File / Folder</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left:2px;">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <!-- Dropdown Import Menu Panel -->
          <div id="import-dropdown" class="import-dropdown hidden">
            <div class="dropdown-header">
              <span>SYSTEM TRACE IMPORTER</span>
            </div>
            
            <div class="dropdown-options">
              <!-- Select File Option -->
              <label class="dropdown-option">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                <div class="option-text">
                  <span class="option-title">Add Trace File</span>
                  <span class="option-desc">Select .trace, .log, or .txt file</span>
                </div>
                <input type="file" id="sys-file-input" accept=".trace,.log,.txt,.out" style="display:none;" />
              </label>

              <!-- Select Folder Option -->
              <label class="dropdown-option">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><polyline points="12 11 12 17"></polyline><polyline points="9 14 15 14"></polyline></svg>
                <div class="option-text">
                  <span class="option-title">Add Trace Folder</span>
                  <span class="option-desc">Select entire gem5 / m5out directory</span>
                </div>
                <input type="file" id="sys-folder-input" webkitdirectory directory multiple style="display:none;" />
              </label>
            </div>

            <!-- Quick Workspace Presets -->
            <div class="dropdown-section-title">WORKSPACE TRACES</div>
            <div class="recent-list">
              <div class="recent-item" data-preset="gem5/m5out/trace.log">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
                <span>gem5/m5out/trace.log</span>
                <span class="preset-tag">Workspace</span>
              </div>
              <div class="recent-item active-preset" data-preset="vmlinux_boot.trace">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
                <span>vmlinux_boot.trace</span>
                <span class="preset-tag">Active</span>
              </div>
            </div>

            <!-- Drag & Drop Zone -->
            <div class="drag-drop-zone" id="drop-zone">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              <span>Drag & drop trace files or folders</span>
            </div>
          </div>
        </div>

        <div class="brand-divider"></div>

        <div class="trace-info">
          <div class="info-item">
            <span class="info-label">TRACE FILE</span>
            <span class="info-val" id="header-file-name">${currentFileName}</span>
          </div>
          <div class="info-item">
            <span class="info-label">BENCHMARK</span>
            <span class="info-val">CoreMark-v1.1</span>
          </div>
          <div class="info-item">
            <span class="info-label">ARCHITECTURE</span>
            <span class="info-val">RISC-V 64-bit / RV64GC</span>
          </div>
          <div class="status-badge-green">
            TRACE LOADED
          </div>
        </div>
      </div>

      <!-- Right Action Tools -->
      <div class="header-right">
        <button class="icon-btn" title="Search trace (Ctrl+F)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </button>
        <button class="icon-btn" id="terminal-toggle-btn" title="Toggle Terminal Log">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
        </button>
       
      </div>
    </div>
  `;

  // Toggle dropdown menu
  const importBtn = container.querySelector('#import-btn');
  const dropdown = container.querySelector('#import-dropdown');

  importBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && !importBtn.contains(e.target)) {
      dropdown.classList.add('hidden');
    }
  });

  // File input change listener
  const sysFileInput = container.querySelector('#sys-file-input');
  sysFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      onFileSelect(file.name, file);
      dropdown.classList.add('hidden');
    }
  });

  // Folder input change listener
  const sysFolderInput = container.querySelector('#sys-folder-input');
  sysFolderInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      const firstFile = files[0];
      const folderName = firstFile.webkitRelativePath.split('/')[0] || 'Selected Folder';
      onFileSelect(`${folderName}/`, files);
      dropdown.classList.add('hidden');
    }
  });

  // Workspace recent preset listener
  container.querySelectorAll('.recent-item').forEach(item => {
    item.addEventListener('click', (e) => {
      const presetName = e.currentTarget.getAttribute('data-preset');
      onFileSelect(presetName);
      dropdown.classList.add('hidden');
    });
  });

  // Drag and drop zone handling
  const dropZone = container.querySelector('#drop-zone');
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  });
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
  });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      if (files.length === 1) {
        onFileSelect(files[0].name, files[0]);
      } else {
        onFileSelect('Dropped Folder/Files', files);
      }
      dropdown.classList.add('hidden');
    }
  });
}
