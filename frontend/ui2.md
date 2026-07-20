# Add Simulation Metrics Section

## Objective

Extend the existing dashboard without increasing visual clutter.

Do not add another row of KPI cards.

Instead create a new section called

Simulation Environment

located directly below the current Trace Summary cards and above CPU Activity.

This section summarizes gem5 simulator execution rather than processor execution.

The layout should follow the same Scientific Minimalism design language.

---

# Section Title

Simulation Environment

Subtitle

Host Performance During Simulation

---

# Layout

Use a responsive 2-column grid.

----------------------------------------------------------

Simulation Timing

Simulation Resources

----------------------------------------------------------

Each panel contains compact metrics.

Avoid large cards.

Use white background.

Thin border.

Soft shadow.

---

# Panel 1

Simulation Timing

Display

simSeconds

hostSeconds

finalTick

simTicks

---

## simSeconds

Title

Simulation Time

Description

Time represented inside the simulated machine.

Visualization

Large numeric value

Small clock icon

Unit

Seconds

Color

Green

---

## hostSeconds

Title

Host Execution Time

Description

Real execution time on host computer.

Visualization

Large numeric value

Small clock icon

Gray

---

## finalTick

Title

Final Tick

Visualization

Mini horizontal timeline

Current simulation end marker

Gray line

Green endpoint

---

## simTicks

Title

Simulation Ticks

Visualization

Mini line chart

Display progression

Use green line

No filled area

---

# Panel 2

Simulation Resources

Display

hostTickRate

hostMemory

simInsts

simOps

---

## hostTickRate

Title

Simulation Speed

Replace Speedometer.

Use horizontal performance bar.

Display

1.45 GTicks/sec

Green progress bar

Target marker

Blue

---

## hostMemory

Title

Host Memory

Replace Gauge.

Use compact memory usage bar.

Display

Used

Available

Percentage

Green

Gray

Avoid circular gauges.

---

## simInsts

Title

Executed Instructions

Visualization

Compact counter

Small trend sparkline

Blue

---

## simOps

Title

Executed Micro Operations

Visualization

Compact counter

Small trend sparkline

Purple

---

# Design Rules

Background

White

Border

#E4E7EB

Radius

12px

Shadow

0 2px 8px rgba(0,0,0,.04)

Spacing

24px

---

# Typography

Title

Inter SemiBold

Metrics

JetBrains Mono

Labels

Inter Regular

---

# Icons

Minimal outline icons only.

Clock

Timing

Memory

RAM

CPU

Simulation

No colorful icons.

---

# Visualization Rules

Replace

Speedometer

↓

Horizontal Progress Bar

Replace

Gauge

↓

Horizontal Resource Bar

Replace

Pie Charts

↓

Stacked Bars

Replace

Large Charts

↓

Compact Sparklines

---

# Color Rules

Simulation Time

Green

Host Time

Gray

Simulation Speed

Blue + Green

Memory Usage

Green

Instructions

Blue

Micro Operations

Purple

Warnings

Amber

Errors

Red

---

# Interaction

Hover any metric

Display tooltip

Click

Open detailed statistics page

Hover charts

Display exact values

---

# UX Goal

The Simulation Environment section should complement the existing CPU metrics.

Users should immediately distinguish between

Processor Execution Statistics

and

Simulator Execution Statistics.

The dashboard should remain clean, spacious, and consistent with Scientific Minimalism.

Avoid adding excessive KPI cards or dashboard clutter.