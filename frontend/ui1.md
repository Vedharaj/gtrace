# GTrace Dashboard Redesign Prompt
## Theme: Scientific Minimalism (Light + Green)

---

# Objective

Redesign the GTrace Dashboard into a modern scientific interface.

The current interface is visually heavy due to the large dark background.

The redesign should create an environment similar to professional engineering software such as

- Apple Xcode
- Linear
- Notion
- Figma
- Arc Browser
- GitHub
- Intel VTune (Light)
- Perfetto (Light)

The interface should feel calm, spacious and natural.

The dashboard should not look like a business analytics dashboard.

Instead it should resemble a CPU architecture analysis tool.

The interface should prioritize readability over decoration.

---

# Design Philosophy

Scientific Minimalism

Characteristics

• Large whitespace

• Flat surfaces

• Thin borders

• Soft shadows

• Very little dark background

• Soft green accents

• Information first

• Calm appearance

The user should immediately focus on processor information rather than colorful cards.

---

# Overall Theme

## Background

Primary Background

#F7F9F8

Secondary Background

#FCFDFC

Panel Background

#FFFFFF

Card Background

#FFFFFF

Sidebar

#F4F7F5

Top Navigation

#FFFFFF

Footer

#F6F8F7

---

# Borders

Use only

1px solid

#E4E7EB

Avoid heavy outlines.

---

# Shadows

Very subtle

box-shadow

0 2px 8px rgba(0,0,0,0.04)

Cards should appear slightly elevated.

---

# Primary Color

Forest Green

#2E7D32

Secondary Green

#4CAF50

Light Green

#A5D6A7

Success

#43A047

Hover

#E8F5E9

Selection

#C8E6C9

---

# Accent Colors

Information

Blue

#2196F3

Warning

Amber

#F9A825

Danger

#E53935

Purple

#7E57C2

These colors should only represent execution events.

Never use them as decorative colors.

---

# Typography

Primary Font

Inter

Numbers

JetBrains Mono

Titles

SemiBold

Body

Regular

Large metrics

32px

Section titles

16px

Labels

13px

---

# Navigation

Replace the dark navigation bar with white.

Use

White background

Thin bottom border

Green underline for active tab

No heavy shadows.

Active page

Green underline

Inactive pages

Gray text

Hover

Light green background

---

# Metric Cards

Current cards are too dark.

Replace with

White cards

Rounded corners

12px radius

Thin border

Soft shadow

Cards should contain

Metric Name

Large Number

Small explanation

Mini sparkline

No icons unless necessary.

---

# Colors for Metrics

Cycles

Dark Gray

Committed Instructions

Blue

Committed Ops

Purple

IPC

Green

CPI

Amber

Execution Time

Gray

Only important values should use color.

---

# CPU Activity

Replace the heavy green rectangle.

Use

Thin horizontal progress bar.

Busy

Green

Idle

Light Gray

Show percentage beside the bar.

Display

User

Kernel

Wait

Interrupt

as compact statistics underneath.

---

# Instruction Commit

Use two horizontal bars.

Instructions

Blue

Micro Ops

Purple

Display values on the right.

Remove large empty spaces.

---

# Execution Timeline

This should become the visual focus.

White background.

Very thin horizontal tracks.

Events

Instruction Commit

Green

Cache Miss

Red

Branch

Purple

Current Cycle

Green vertical line

Pipeline Stall

Amber

Grid lines

Very light gray.

Timeline should resemble

Perfetto

Chrome Trace Viewer

Intel VTune

---

# White Space

Increase spacing between sections.

Minimum spacing

24px

Avoid filling every area.

Allow breathing room.

---

# Icons

Use simple outline icons only.

Stroke width

1.5px

No filled icons.

No colorful icons.

---

# Animations

Hover

150ms

Progress Bar

250ms

Timeline Cursor

Smooth

Card Hover

Small elevation

No bouncing animations.

---

# Sidebar

Background

#F4F7F5

Active Item

Green background

Green icon

Inactive Item

Gray

Hover

Light green

Remove the dark sidebar.

---

# Search Bar

White background

Rounded

Thin gray border

Green focus border

Placeholder

Search trace...

---

# Header

White

Minimal

Display

Trace File

Benchmark

Architecture

Status

Use green badge

TRACE LOADED

---

# Status Colors

Ready

Green

Processing

Amber

Error

Red

Paused

Gray

---

# Dashboard Layout

--------------------------------------------------------

Header

--------------------------------------------------------

Quick Metrics

Cycles

Instructions

Committed Ops

IPC

CPI

Execution Time

--------------------------------------------------------

CPU Activity

Instruction Commit

--------------------------------------------------------

Execution Timeline

--------------------------------------------------------

Footer

--------------------------------------------------------

Everything should align to an 8px spacing grid.

---

# UX Goals

The dashboard should feel

calm

minimal

professional

engineering-focused

easy to read

Users should understand execution metrics within five seconds.

Avoid visual clutter.

Avoid unnecessary decorations.

The interface should resemble professional engineering software rather than a business analytics dashboard.

The emphasis should always remain on CPU execution analysis and trace exploration.
