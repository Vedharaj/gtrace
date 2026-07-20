export function renderSidebar(container, activeView, isCollapsed, onSelectView, onToggleCollapse) {
  const analysisNav = [
    { id: 'dashboard', label: 'Dashboard', icon: '<rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect>' },
    { id: 'editor', label: 'Editor', icon: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><polyline points="10 13 8 15 10 17"></polyline><polyline points="14 13 16 15 14 17"></polyline>' },
    { id: 'datapath', label: 'Datapath', icon: '<rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line>' },
    { id: 'memory', label: 'Memory', icon: '<path d="M6 19v-3M10 19v-3M14 19v-3M18 19v-3M6 8V5M10 8V5M14 8V5M18 8V5"></path><rect x="2" y="8" width="20" height="8" rx="2"></rect>' },
    { id: 'cache', label: 'Cache', icon: '<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>' }
  ];

  const advancedNav = [
    { id: 'registers', label: 'Registers', icon: '<line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>' },
    { id: 'pipeline', label: 'Pipeline', icon: '<rect x="3" y="3" width="6" height="6" rx="1"></rect><rect x="15" y="3" width="6" height="6" rx="1"></rect><rect x="9" y="15" width="6" height="6" rx="1"></rect><path d="M6 9v3a1 1 0 0 0 1 1h4"></path><path d="M18 9v3a1 1 0 0 1-1 1h-4"></path>' },
    { id: 'branch', label: 'Branch Predictor', icon: '<line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path>' },
    { id: 'statistics', label: 'Statistics', icon: '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>' }
  ];

  const bottomNav = [
    { id: 'settings', label: 'Settings', icon: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>' },
    { id: 'help', label: 'Help', icon: '<circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line>' }
  ];

  container.className = `sidebar ${isCollapsed ? 'collapsed' : ''}`;

  container.innerHTML = `
    <!-- Top Sidebar Brand & Pulse Logo -->
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--green-primary)" stroke-width="2.5">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        <span class="logo-title">GTrace</span>
      </div>
      <button class="collapse-btn" id="sidebar-toggle-btn" title="${isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          ${isCollapsed ? '<polyline points="13 17 18 12 13 7"></polyline><polyline points="6 17 11 12 6 7"></polyline>' : '<polyline points="11 17 6 12 11 7"></polyline><polyline points="18 17 13 12 18 7"></polyline>'}
        </svg>
      </button>
    </div>

    <!-- Navigation Scroll Region -->
    <div class="sidebar-body">
      <!-- Section 1: Analysis -->
      <div class="nav-section">
        <div class="section-header">ANALYSIS</div>
        <div class="nav-group">
          ${analysisNav.map(item => `
            <button class="nav-item ${activeView === item.id ? 'active' : ''}" data-view="${item.id}" title="${item.label}">
              <div class="active-indicator"></div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">${item.icon}</svg>
              <span class="nav-label">${item.label}</span>
            </button>
          `).join('')}
        </div>
      </div>

      <!-- Section 2: Advanced Analysis -->
      <div class="nav-section">
        <div class="section-header">ADVANCED ANALYSIS</div>
        <div class="nav-group">
          ${advancedNav.map(item => `
            <button class="nav-item ${activeView === item.id ? 'active' : ''}" data-view="${item.id}" title="${item.label}">
              <div class="active-indicator"></div>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">${item.icon}</svg>
              <span class="nav-label">${item.label}</span>
            </button>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Bottom Section: Settings & Help -->
    <div class="sidebar-footer">
      <div class="nav-group">
        ${bottomNav.map(item => `
          <button class="nav-item ${activeView === item.id ? 'active' : ''}" data-view="${item.id}" title="${item.label}">
            <div class="active-indicator"></div>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">${item.icon}</svg>
            <span class="nav-label">${item.label}</span>
          </button>
        `).join('')}
      </div>
    </div>
  `;

  // Item click listener
  container.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const viewId = e.currentTarget.getAttribute('data-view');
      onSelectView(viewId);
    });
  });

  // Collapse toggle listener
  const toggleBtn = container.querySelector('#sidebar-toggle-btn');
  toggleBtn.addEventListener('click', onToggleCollapse);
}
