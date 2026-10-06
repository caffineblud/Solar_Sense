<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&duration=3200&pause=1000&color=FF8C00&center=true&vCenter=true&width=760&lines=SolarSense;AI+Smart+Energy+Manager;Forecast+%C2%B7+Schedule+%C2%B7+Protect;Smart+India+Hackathon+2026" alt="SolarSense typing banner" />

<br>

![Status](https://img.shields.io/badge/Status-Working_Prototype-FF8C00?style=flat-square)
![SIH](https://img.shields.io/badge/SIH-2026-1a1b26?style=flat-square&labelColor=FF8C00)
![Problem](https://img.shields.io/badge/Problem_Statement-SIH26200-FF8C00?style=flat-square)
![Category](https://img.shields.io/badge/Category-Software-1a1b26?style=flat-square)
![Theme](https://img.shields.io/badge/Theme-Renewable_Energy-1f8a4c?style=flat-square)

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![SVG](https://img.shields.io/badge/Charts-Inline_SVG-FF8C00?style=flat-square)
![Dependencies](https://img.shields.io/badge/Dependencies-0-1f8a4c?style=flat-square)
![Languages](https://img.shields.io/badge/UI-English_%7C_%E0%A4%B9%E0%A4%BF%E0%A4%A8%E0%A5%8D%E0%A4%A6%E0%A5%80-1a1b26?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-FF8C00?style=flat-square)

**Predict solar output, schedule loads and batteries, and catch faulty panels, with software alone.**

[Live Demo](https://caffineblud.github.io/SolarSense/) · [Features](#features) · [Quick Start](#quick-start) · [How It Works](#how-it-works) · [Roadmap](#roadmap)

![Visitors](https://komarev.com/ghpvc/?username=caffineblud-solarsense&label=Visitors&color=FF8C00&style=flat-square)

</div>

---

## Overview

Solar output rises and falls with weather and time of day. Sites with solar panels and a battery often waste surplus energy, buy expensive evening grid power, or lose output to dust and faults they never notice.

**SolarSense** is an AI-based energy manager for solar-plus-battery sites such as campuses, MSMEs, farms and villages. It works on the inverter and meter data a site already has, so no new hardware is needed.

This repository holds the **working prototype**: a single HTML file running on simulated data, built for the Smart India Hackathon 2026.

> [!NOTE]
> All numbers in the prototype come from a built-in simulation. It shows how the product behaves; it does not read real inverters yet.

---

## Status Board

| | |
|:--|:--|
| **Team** | The Digital Artisans (ID `140147`) |
| **Problem Statement** | `SIH26200` · Student Innovation, renewable / sustainable energy |
| **Category** | Software |
| **Technology Bucket** | AI/ML, Cloud Computing, Blockchain |
| **Prototype** | Single file, no build step, no backend |
| **Size** | about 31 KB |
| **Languages** | English and Hindi, switchable live |
| **Themes** | Light and dark, remembered between visits |

---

## Features

| Screen | What you can do |
|:--|:--|
| **Dashboard** | Watch a sun cross the sky as the clock moves. Live solar output, demand, battery %, grid draw, rupees saved and CO₂ avoided. Chart shows solar vs demand for the day. |
| **Forecast** | 48-hour solar forecast with a confidence band. Switch between Clear, Cloudy and Monsoon to see accuracy and uncertainty change. |
| **Optimiser** | Compare Usual vs Optimised schedules. Hour-by-hour strip shows when the site runs on solar, charges, discharges or uses the grid. Each load shows a plain-language reason. |
| **Panel Health** | 12 panels coloured by efficiency, anomaly score per panel, dust alerts, **Simulate dust** and **Mark as cleaned** buttons. |
| **Community** | Three neighbouring sites with live surplus or shortfall, and suggested peer-to-peer energy shares you can accept. |
| **Impact** | Monthly savings, solar used on site, CO₂ avoided, trees equivalent, and a 6-month savings chart. |

### Across the whole app

- **Run demo** replays a full 24-hour day in seconds.
- **Offline mode** switch shows the edge-mode banner: *Running on local edge mode, will sync when online*.
- **Hindi / English** toggle translates every label, reason and alert.
- **Touch or hover** any chart for exact values. Click the dashboard chart to move the clock.
- Mobile bottom tabs and a desktop sidebar, with keyboard focus styles.

---

## Prototype vs Planned Product

| Capability | Prototype (this repo) | Planned product |
|:--|:--:|:--:|
| Solar and demand forecast | Simulated curves | XGBoost, LSTM, pvlib model |
| Weather data | Clear / Cloudy / Monsoon presets | Open-Meteo, NASA POWER |
| Load and battery scheduling | Rule-based hourly plan | Cost and carbon optimiser |
| Panel fault detection | Efficiency threshold and anomaly score | Isolation Forest on inverter data |
| Explanations | Written reasons per load | SHAP-backed plain-language advice |
| Offline edge mode | UI banner | Local scheduling, later sync |
| Community sharing | Suggested transfers, accept button | Metered peer-to-peer sharing |
| Backend and storage | None | FastAPI, TimescaleDB, MQTT |
| Apps | One responsive web page | React dashboard and Flutter app |
| Security | n/a | MFA, encrypted storage, RBAC |

---

## Quick Start

No installation and no dependencies.

```bash
# 1. Clone
git clone https://github.com/caffineblud/SolarSense.git
cd SolarSense

# 2. Open directly
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux

# 3. Or serve locally
python -m http.server 8000
# then visit http://localhost:8000
```

> [!TIP]
> Press **Run demo** first to watch a full day play out, then try the weather buttons on the Forecast tab.

---

## How It Works

```mermaid
flowchart LR
    A[Inverter, meter and weather data] --> B[Simulation engine]
    B --> C[Solar and demand forecast]
    C --> D[Optimiser: loads, battery, grid]
    B --> E[Panel health and anomaly score]
    D --> F[Dashboard and alerts]
    E --> F
    D --> G[Community sharing]
    F --> H[Savings and CO2 impact]
```

### Simulation model

| Parameter | Value used in the prototype |
|:--|:--|
| Solar array | 12 panels, about 12 kW peak |
| Weather factor | Clear `1.0` · Cloudy `0.5` · Monsoon `0.25` |
| Forecast accuracy shown | 94% · 86% · 77% |
| Battery | 20 kWh, 3 kWh reserve kept |
| Grid price | ₹7/kWh, ₹9/kWh at evening peak (6 to 10 pm) |
| Grid carbon factor | 0.82 kg CO₂ per kWh |
| Peer-to-peer price | ₹5/kWh vs ₹8/kWh grid |
| Panel colour bands | green ≥ 93% · amber 85 to 92% · red < 85% |

### Shiftable loads

| Load | Power | Usual time | Optimised time |
|:--|:--:|:--:|:--:|
| Water pump | 2.2 kW | 06:00 to 08:00 | 11:00 to 13:00 |
| EV charger | 3.3 kW | 19:00 to 22:00 | 12:00 to 15:00 |
| Washing machine | 1.0 kW | 20:00 to 21:00 | 13:00 to 14:00 |
| AC pre-cooling | 1.8 kW | 18:00 to 20:00 | 15:00 to 17:00 |

### Hour-by-hour modes

| Mode | Meaning |
|:--|:--|
| Running on solar | Solar covers demand |
| Battery charging | Surplus solar fills the battery |
| Battery discharging | Battery covers demand, usually in the evening |
| Using grid | Solar and battery are not enough |

---

## Project Structure

```text
SolarSense/
├── index.html      # the whole prototype: markup, styles and script
├── README.md
├── assets/         # screenshots and demo gif (add your own)
└── docs/           # SIH presentation PDF and synopsis
```

---

## Tech Stack

| Layer | Prototype | Planned |
|:--|:--|:--|
| Frontend | HTML, CSS, vanilla JavaScript | React, Flutter |
| Charts | Hand-drawn inline SVG | Same approach, live data |
| Fonts | Outfit, Noto Sans Devanagari | Same |
| Backend | none | Python, FastAPI |
| Data | in-memory simulation | TimescaleDB, MQTT |
| AI / ML | rule-based simulation | XGBoost, LSTM, Isolation Forest, SHAP, pvlib |
| Deployment | GitHub Pages | Docker on cloud or edge |

---

## Roadmap

- [x] Six-screen interactive prototype
- [x] Hindi and English
- [x] Light and dark themes
- [x] Offline edge-mode banner
- [ ] Replace simulated curves with real weather data
- [ ] Train forecasting models on public solar datasets
- [ ] Read live data from inverters over MQTT or Modbus
- [ ] Real fault detection with Isolation Forest
- [ ] React dashboard and Flutter mobile app
- [ ] Pilot on a campus solar setup

---

## Version History

| Version | Stage | Notes |
|:--|:--|:--|
| `v0.1` | Concept | SIH idea presentation and portal submission |
| `v0.2` | First prototype | Dashboard, forecast, optimiser, panels, community, impact |
| `v1.0` | Current prototype | Hour-by-hour plan, dust simulation, accept-share flow, 6-month chart, day and night sun scene, light and dark themes, saved language |

---

## Team

<div align="center">

**The Digital Artisans** · Team ID `140147`

[![GitHub](https://img.shields.io/badge/GitHub-caffineblud-1a1b26?style=flat-square&logo=github&logoColor=FF8C00)](https://github.com/caffineblud)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-yashsingh200606-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/yashsingh200606)
[![LeetCode](https://img.shields.io/badge/LeetCode-Yashsingh200606-FF8C00?style=flat-square&logo=leetcode&logoColor=white)](https://leetcode.com/Yashsingh200606)

<br>

<img src="https://github-readme-stats.vercel.app/api?username=caffineblud&show_icons=true&theme=tokyonight&hide_border=true&title_color=FF8C00&icon_color=FF8C00" height="150" alt="GitHub stats" />
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=caffineblud&layout=compact&theme=tokyonight&hide_border=true&title_color=FF8C00" height="150" alt="Top languages" />

</div>

---

## Contributing

Ideas and fixes are welcome.

```bash
git checkout -b feature/your-idea
git commit -m "Add your idea"
git push origin feature/your-idea
```

Then open a pull request.

---

## License

Released under the [MIT License](LICENSE).

<div align="center">

**Built for Smart India Hackathon 2026**

*Less guessing, more sunlight used.*

</div>
