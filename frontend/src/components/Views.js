export function renderEditorView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title" style="display: flex; justify-content: space-between; align-items: center;">
        <span>Source & RISC-V Assembly Disassembly Editor</span>
        <div style="display: flex; gap: 8px;">
          <input type="text" placeholder="Search instruction (e.g. jal, addi)..." style="padding: 4px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; font-family: var(--font-mono); width: 220px;" />
          <span class="status-badge-green">PC: 0x102b2</span>
        </div>
      </div>

      <div class="grid-2" style="grid-template-columns: 1fr 1fr;">
        <!-- C Source Code View -->
        <div class="card-sub">
          <div class="card-sub-title" style="display: flex; justify-content: space-between;">
            <span>coremark_main.c</span>
            <span class="mono-dim">Line 42</span>
          </div>
          <div style="font-family: var(--font-mono); font-size: 11px; line-height: 1.8; background-color: #FFFFFF; border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; overflow-x: auto;">
            <div style="color: #64748B;">// CoreMark benchmark entry point</div>
            <div><span style="color: #2563EB;">int</span> main(<span style="color: #2563EB;">int</span> argc, <span style="color: #2563EB;">char</span> *argv[]) {</div>
            <div>  ee_u32 i, j;</div>
            <div>  core_results results;</div>
            <div style="background-color: var(--green-hover); color: var(--green-primary); font-weight: 600; padding: 2px 4px; border-radius: 3px;">► core_list_init(&results, count, seed);</div>
            <div>  matrix_init(matrix_size, matrix_buffer);</div>
            <div>  crc_calc(crc_buffer, crc_size);</div>
            <div>  return 0;</div>
            <div>}</div>
          </div>
        </div>

        <!-- Disassembly View -->
        <div class="card-sub">
          <div class="card-sub-title" style="display: flex; justify-content: space-between;">
            <span>RISC-V Disassembly (RV64GC)</span>
            <span class="mono-dim">Trace Line 8/23</span>
          </div>
          <div style="font-family: var(--font-mono); font-size: 11px; line-height: 1.8; background-color: #FFFFFF; border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; overflow-x: auto;">
            <div style="color: #64748B;">0x102a4: jal     ra, 44               <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div style="color: #64748B;">0x102d0: auipc   gp, 108              <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div style="color: #64748B;">0x102d4: addi    gp, gp, -480         <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div style="color: #64748B;">0x102a8: c_mv    a5, a0               <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div style="background-color: var(--green-hover); color: var(--green-primary); font-weight: 700; padding: 2px 4px; border-radius: 3px; border-left: 3px solid var(--green-primary);">► 0x102b2: c_ldsp  a1, 0(sp)          (MemRead)  [D=0x1 A=0x7fffffff]</div>
            <div>0x102b4: c_addi4spn a2, sp, 8     <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div>0x102b6: andi    sp, sp, -16          <span style="color: var(--color-blue);">(IntAlu)</span></div>
            <div>0x102ba: auipc   a3, 0                <span style="color: var(--color-blue);">(IntAlu)</span></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderDatapathView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">5-Stage Pipeline CPU Datapath Visualizer</div>
      
      <div class="card-sub" style="background-color: #FFFFFF;">
        <div class="card-sub-title">Pipeline Stage Movement (IF → ID → EX → MEM → WB)</div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin: 20px 0;">
          <!-- Stage 1: Fetch -->
          <div style="flex: 1; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; background-color: var(--bg-primary); text-align: center;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">IF (Instruction Fetch)</div>
            <div class="mono" style="font-size: 13px; font-weight: 700; color: var(--color-blue); margin-top: 6px;">0x102b4</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">c_addi4spn</div>
          </div>

          <div style="color: var(--green-primary); font-size: 18px;">➔</div>

          <!-- Stage 2: Decode -->
          <div style="flex: 1; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; background-color: var(--bg-primary); text-align: center;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">ID (Instruction Decode)</div>
            <div class="mono" style="font-size: 13px; font-weight: 700; color: var(--color-purple); margin-top: 6px;">rs1=sp, rd=a1</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">Register Read</div>
          </div>

          <div style="color: var(--green-primary); font-size: 18px;">➔</div>

          <!-- Stage 3: Execute -->
          <div style="flex: 1; border: 1px solid var(--green-primary); border-radius: 8px; padding: 14px; background-color: var(--green-hover); text-align: center;">
            <div style="font-size: 11px; font-weight: 700; color: var(--green-primary);">EX (ALU Execution)</div>
            <div class="mono" style="font-size: 13px; font-weight: 700; color: var(--green-primary); margin-top: 6px;">Addr Calc</div>
            <div style="font-size: 10px; color: var(--green-primary); margin-top: 2px;">ACTIVE STAGE</div>
          </div>

          <div style="color: var(--green-primary); font-size: 18px;">➔</div>

          <!-- Stage 4: Memory -->
          <div style="flex: 1; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; background-color: var(--bg-primary); text-align: center;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">MEM (Memory Access)</div>
            <div class="mono" style="font-size: 13px; font-weight: 700; color: var(--color-amber); margin-top: 6px;">L1D Read</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">0x7fffffff20</div>
          </div>

          <div style="color: var(--green-primary); font-size: 18px;">➔</div>

          <!-- Stage 5: Writeback -->
          <div style="flex: 1; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; background-color: var(--bg-primary); text-align: center;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted);">WB (Writeback)</div>
            <div class="mono" style="font-size: 13px; font-weight: 700; color: var(--text-primary); margin-top: 6px;">a1 = 0x1</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">Commit</div>
          </div>
        </div>

        <div class="grid-2">
          <div class="card-sub">
            <div class="card-sub-title">Forwarding & Hazard Unit</div>
            <div style="font-size: 12px; color: var(--text-secondary); display: flex; flex-direction: column; gap: 8px;">
              <div style="display: flex; justify-content: space-between;"><span>EX/MEM Forwarding:</span><span class="mono" style="color: var(--green-primary); font-weight: 600;">ACTIVE (rs1 -> EX)</span></div>
              <div style="display: flex; justify-content: space-between;"><span>MEM/WB Forwarding:</span><span class="mono">INACTIVE</span></div>
              <div style="display: flex; justify-content: space-between;"><span>Load-Use Hazard Stall:</span><span class="mono" style="color: var(--color-amber); font-weight: 600;">0 Cycles</span></div>
            </div>
          </div>

          <div class="card-sub">
            <div class="card-sub-title">ALU Control Status</div>
            <div style="font-size: 12px; color: var(--text-secondary); display: flex; flex-direction: column; gap: 8px;">
              <div style="display: flex; justify-content: space-between;"><span>ALU Operation:</span><span class="mono" style="font-weight: 600;">ADD (Addr Offset)</span></div>
              <div style="display: flex; justify-content: space-between;"><span>Operand A:</span><span class="mono">0x7fffffffffffff20</span></div>
              <div style="display: flex; justify-content: space-between;"><span>Operand B:</span><span class="mono">0x0000000000000000</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderMemoryView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">Runtime Memory Layout & Address Inspector</div>
      
      <div class="grid-2">
        <!-- Memory Map -->
        <div class="card-sub">
          <div class="card-sub-title">Virtual Address Space Regions</div>
          <table style="width: 100%; text-align: left; font-family: var(--font-mono); font-size: 11px; border-collapse: collapse;">
            <thead>
              <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border-color);">
                <th style="padding: 8px;">REGION</th><th style="padding: 8px;">START ADDR</th><th style="padding: 8px;">END ADDR</th><th style="padding: 8px;">PERM</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom: 1px solid var(--border-light);">
                <td style="padding: 8px; color: var(--color-blue); font-weight: 600;">Stack</td><td>0x7fffffff0000</td><td>0x7fffffffffff</td><td>r-w-</td>
              </tr>
              <tr style="border-bottom: 1px solid var(--border-light);">
                <td style="padding: 8px; color: var(--green-primary); font-weight: 600;">Heap</td><td>0x10048000</td><td>0x10090000</td><td>r-w-</td>
              </tr>
              <tr style="border-bottom: 1px solid var(--border-light);">
                <td style="padding: 8px; color: var(--color-amber); font-weight: 600;">.data / .bss</td><td>0x10040000</td><td>0x10048000</td><td>r-w-</td>
              </tr>
              <tr>
                <td style="padding: 8px; color: var(--color-purple); font-weight: 600;">.text (Code)</td><td>0x10000000</td><td>0x10040000</td><td>r-x</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Address Access Timeline -->
        <div class="card-sub">
          <div class="card-sub-title">Recent Load / Store Operations</div>
          <div style="font-family: var(--font-mono); font-size: 11px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; padding: 6px; background-color: var(--green-hover); border-radius: 4px;">
              <span style="color: var(--green-primary); font-weight: 600;">READ [0x7fffffffffffff20]</span>
              <span>VAL: 0x00000001</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px; background-color: #F1F5F9; border-radius: 4px;">
              <span style="color: var(--color-purple); font-weight: 600;">WRITE [0x7fffffffffffff10]</span>
              <span>VAL: 0x00000000</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 6px; background-color: #F1F5F9; border-radius: 4px;">
              <span style="color: var(--color-blue); font-weight: 600;">READ [0x10048000]</span>
              <span>VAL: 0x400921fb</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderCacheView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">Cache Hierarchy & Hit / Miss Visualizer</div>
      
      <div class="card-sub" style="background-color: #FFFFFF;">
        <div class="card-sub-title">Animated Cache Access Pipeline</div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; margin: 24px 0;">
          <!-- CPU Core -->
          <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; width: 140px; text-align: center; background-color: var(--bg-primary);">
            <div style="font-weight: 700; font-size: 13px;">Core-0 CPU</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">RISC-V 64-bit</div>
          </div>

          <div style="color: var(--green-primary); font-size: 20px;">➔</div>

          <!-- L1 Caches -->
          <div style="display: flex; flex-direction: column; gap: 12px;">
            <div style="border: 1px solid var(--green-primary); background-color: var(--green-hover); border-radius: 6px; padding: 10px 16px; text-align: center;">
              <div style="font-weight: 700; font-size: 11px; color: var(--green-primary);">L1 I-Cache (32KB)</div>
              <div style="font-size: 10px; color: var(--green-primary);">HIT RATE: 99.86%</div>
            </div>
            <div style="border: 1px solid var(--green-primary); background-color: var(--green-hover); border-radius: 6px; padding: 10px 16px; text-align: center;">
              <div style="font-weight: 700; font-size: 11px; color: var(--green-primary);">L1 D-Cache (32KB)</div>
              <div style="font-size: 10px; color: var(--green-primary);">HIT RATE: 98.04%</div>
            </div>
          </div>

          <div style="color: var(--green-primary); font-size: 20px;">➔</div>

          <!-- L2 Cache -->
          <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; width: 140px; text-align: center; background-color: var(--bg-primary);">
            <div style="font-weight: 700; font-size: 12px;">L2 Cache (512KB)</div>
            <div style="font-size: 10px; color: var(--color-purple); margin-top: 2px;">HIT RATE: 90.69%</div>
          </div>

          <div style="color: var(--green-primary); font-size: 20px;">➔</div>

          <!-- Main Memory DRAM -->
          <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; width: 140px; text-align: center; background-color: var(--bg-primary);">
            <div style="font-weight: 700; font-size: 12px;">Main DRAM</div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 2px;">DDR4-2400</div>
          </div>
        </div>

        <div class="grid-2">
          <div class="card-sub">
            <div class="card-sub-title">Event Status Legend</div>
            <div style="display: flex; gap: 16px; font-size: 12px; font-weight: 600;">
              <span style="color: var(--green-primary);">● CACHE HIT</span>
              <span style="color: var(--color-red);">● CACHE MISS</span>
              <span style="color: var(--color-amber);">● EVICTION</span>
            </div>
          </div>

          <div class="card-sub">
            <div class="card-sub-title">Average Access Latencies</div>
            <div style="font-family: var(--font-mono); font-size: 11px; display: flex; justify-content: space-between;">
              <span>L1: 1 cycle (0.5ns)</span>
              <span>L2: 12 cycles (6ns)</span>
              <span>DRAM: 85 cycles (42.5ns)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderRegistersView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">RISC-V Integer & Floating Point Register File</div>
      <div class="grid-2">
        <div class="card-sub">
          <div class="card-sub-title">Integer Registers (x0 - x31)</div>
          <table style="width: 100%; text-align: left; font-family: var(--font-mono); font-size: 11px;">
            <tr style="border-bottom: 1px solid var(--border-light);"><td>ra (x1)</td><td>0x00000000000102a8</td></tr>
            <tr style="border-bottom: 1px solid var(--border-light);"><td>sp (x2)</td><td>0x7fffffffffffff20</td></tr>
            <tr style="border-bottom: 1px solid var(--border-light);"><td>gp (x3)</td><td>0x000000000007c0f0</td></tr>
            <tr style="border-bottom: 1px solid var(--border-light); color: var(--green-primary); font-weight: 700;"><td>a0 (x10)</td><td>0x0000000000010392</td></tr>
            <tr><td>a1 (x11)</td><td>0x0000000000000001</td></tr>
          </table>
        </div>
        <div class="card-sub">
          <div class="card-sub-title">Floating Point Registers (f0 - f31)</div>
          <table style="width: 100%; text-align: left; font-family: var(--font-mono); font-size: 11px;">
            <tr style="border-bottom: 1px solid var(--border-light);"><td>ft0 (f0)</td><td>0x400921fb54442d18 (3.14159)</td></tr>
            <tr style="border-bottom: 1px solid var(--border-light);"><td>ft1 (f1)</td><td>0x0000000000000000 (0.0)</td></tr>
            <tr><td>fa0 (f10)</td><td>0x3ff0000000000000 (1.0)</td></tr>
          </table>
        </div>
      </div>
    </div>
  `;
}

export function renderPipelineView(container, state) {
  renderDatapathView(container, state);
}

export function renderBranchView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">Branch Predictor & Target Buffer (BTB) Analysis</div>
      <div class="grid-2">
        <div class="card-sub">
          <div class="card-sub-title">Branch Prediction Metrics</div>
          <div class="activity-stats" style="grid-template-columns: 1fr 1fr; border-top: none; padding-top: 0;">
            <div class="stat-item"><span class="stat-label">TOTAL BRANCHES</span><span class="stat-val">230,794</span></div>
            <div class="stat-item"><span class="stat-label">ACCURACY</span><span class="stat-val" style="color: var(--green-primary);">95.2%</span></div>
            <div class="stat-item"><span class="stat-label">MISPREDICTIONS</span><span class="stat-val" style="color: var(--color-amber);">11,078</span></div>
            <div class="stat-item"><span class="stat-label">BTB HIT RATE</span><span class="stat-val">98.4%</span></div>
          </div>
        </div>
        <div class="card-sub">
          <div class="card-sub-title">Predictor Scheme</div>
          <div style="font-size: 12px; color: var(--text-secondary);">
            <div>Type: <strong>2-bit saturating counter</strong></div>
            <div style="margin-top: 6px;">BTB Entries: <strong>4096 entries</strong></div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function renderStatisticsView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">gem5 Detailed Simulation Statistics</div>
      <div class="card-sub">
        <div class="card-sub-title">System Execution Summary</div>
        <div class="activity-stats" style="grid-template-columns: 1fr 1fr 1fr 1fr; border-top: none; padding-top: 0;">
          <div class="stat-item"><span class="stat-label">TOTAL TICKS</span><span class="stat-val">4,102,931,000</span></div>
          <div class="stat-item"><span class="stat-label">COMMITTED INSTS</span><span class="stat-val">2,913,004</span></div>
          <div class="stat-item"><span class="stat-label">IPC</span><span class="stat-val" style="color: var(--green-primary);">0.71</span></div>
          <div class="stat-item"><span class="stat-label">CPI</span><span class="stat-val" style="color: var(--color-amber);">1.42</span></div>
        </div>
      </div>
    </div>
  `;
}

export function renderSettingsView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">GTrace Preferences & Configuration</div>
      <div class="card-sub">
        <div class="card-sub-title">Appearance & Theme</div>
        <div style="font-size: 12px; color: var(--text-secondary);">
          Theme: <strong>Scientific Minimalism (Light + Green)</strong>
        </div>
      </div>
    </div>
  `;
}

export function renderHelpView(container, state) {
  container.innerHTML = `
    <div class="view-panel">
      <div class="view-header-title">GTrace Help & Documentation</div>
      <div class="card-sub">
        <div class="card-sub-title">Quick Shortcuts</div>
        <div style="font-size: 12px; color: var(--text-secondary); display: flex; flex-direction: column; gap: 8px;">
          <div><strong>Ctrl + F</strong>: Search trace instructions</div>
          <div><strong>Drag Timeline Scrubber</strong>: Scrub simulation cycles</div>
        </div>
      </div>
    </div>
  `;
}
