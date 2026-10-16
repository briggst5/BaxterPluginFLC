# VS100CR Design Requirements & Referral Logic

> Sources: DID 60064652 (Design Input Document, Rev T), SRS 60064749 (Rev Y Final)
> Authors: Robert Rogers, William Shampine et al. (Baxter / Welch Allyn)

---

## Intended Use

The **Spot Vision Screener** produces optical images to help identify refractive errors and ocular misalignments by detecting NIR light reflexes from each eye. It estimates refractive error, pupil size, pupil distance, and gaze deviation. Intended for subjects **6 months through adults**. Not a replacement for a full eye exam — a screening tool to determine if referral to an eye care specialist is warranted.

Cleared for use by healthcare professionals or under direction of a healthcare professional.

---

## Clinical Measurement Requirements

### 1. Spherical Equivalent / Sphere (DID Req 1, 34)
| Property | Value |
|----------|-------|
| Range | −7.50 D to +7.50 D |
| Resolution | 0.25 D increments |
| Accuracy (−3.50 to +3.50 D) | ±0.50 D mean; 50% of readings within ±1.00 D |
| Accuracy (>3.50 or <−3.50 D) | ±1.00 D mean; 50% of readings within ±2.00 D |

### 2. Cylinder (DID Req 2, 35)
| Property | Value |
|----------|-------|
| Range | 0.00 to +3.00 D (reportable as + or − cylinder) |
| Resolution | 0.25 D increments |
| Accuracy (0–1.50 D) | ±0.50 D mean; 50% within ±1.00 D |
| Accuracy (1.50–3.00 D) | ±1.00 D mean; 50% within ±2.00 D |

### 3. Cylinder Axis (DID Req 3, 36)
| Property | Value |
|----------|-------|
| Range | 1 to 180 degrees |
| Resolution | 1 degree |
| Accuracy (for Cyl > 0.5 D) | ±10 degrees mean; 50% within ±20 degrees |

### 4. Gaze / Corneal Light Reflex (DID Req 4, 37)
| Property | Value |
|----------|-------|
| Range | 0–20° Nasal(N) or Temporal(T), 0–20° Inferior(I) or Superior(S) |
| Resolution | 1 degree |
| Accuracy | ±1.5 degrees mean; 50% within ±3.0 degrees |

### 5. Interpupillary Distance / IPD (DID Req 5, 38)
| Property | Value |
|----------|-------|
| Range | 35.0 to 80.0 mm |
| Resolution | 1 mm (display) / 0.1 mm (printed) |
| Accuracy | ±1.5 mm mean; 50% within ±3.0 mm |

### 6. Pupil Size / Diameter (DID Req 6, 39)
| Property | Value |
|----------|-------|
| Range (SW ≥ 3.1.00.00-A0004, age 6–239 months) | 4.00 to 9.00 mm |
| Range (SW ≥ 3.1.00.00-A0004, age 240–1200 months) | 3.00 to 9.00 mm |
| Range (SW < 3.1.00.00-A0004, all ages) | 4.00 to 9.00 mm |
| Resolution | 0.1 mm |
| Accuracy | ±0.4 mm mean; 50% within ±0.8 mm |

---

## Reference Threshold Analysis (Referral Logic)

All thresholds are **age-stratified** and are compared against measured values to produce a **Within Range / Outside Range** flag per eye (OD/OS). Default thresholds are configurable by the user.

### 7. Anisometropia (DID Req 7)
Condition: |SphericalEquivalent(OD) − SphericalEquivalent(OS)| ≥ threshold → Outside Range

| Age Range | Default Threshold (D) |
|-----------|----------------------|
| 6 months to <1 year | 1.5 |
| 1 year to <3 years | 1.0 |
| 3 years to <6 years | 1.0 |
| 6 years to <20 years | 1.0 |
| >20 years | 1.0 |

### 8. Myopia (DID Req 8)
Condition: SphericalEquivalent(OD/OS) ≤ threshold → Outside Range

| Age Range | Threshold (SW ≥ 3.1.00.00-A0004) | Threshold (SW < 3.1.00.00-A0004) |
|-----------|-----------------------------------|-----------------------------------|
| 6 mo to <1 yr | −2.0 | −2.0 |
| 1 yr to <3 yr | −2.0 | −2.0 |
| 3 yr to <6 yr | −1.25 | −1.25 |
| 6 yr to <20 yr | −1.0 | −1.0 |
| >20 yr | −1.5 | −0.75 |

### 9. Hyperopia (DID Req 9)
Condition: SphericalEquivalent(OD/OS) ≥ threshold → Outside Range

| Age Range | Default Threshold (D) |
|-----------|----------------------|
| 6 mo to <1 yr | 3.5 |
| 1 yr to <3 yr | 3.0 |
| 3 yr to <6 yr | 2.5 |
| 6 yr to <20 yr | 2.5 |
| >20 yr | 1.5 |

### 10. Astigmatism (DID Req 10)
Condition: |Cylinder(OD/OS)| ≥ threshold → Outside Range

| Age Range | Default Threshold (D) |
|-----------|----------------------|
| 6 mo to <1 yr | 2.25 |
| 1 yr to <3 yr | 2.0 |
| 3 yr to <6 yr | 1.75 |
| 6 yr to <20 yr | 1.5 |
| >20 yr | 1.5 |

### 11. Anisocoria (DID Req 11)
Condition: |PupilSize(OD) − PupilSize(OS)| ≥ threshold → Outside Range

| Age Range | Default Threshold (mm) |
|-----------|----------------------|
| All ages | 1.0 |

### 12. Strabismus / Gaze (DID Req 12)
Condition: |CorneaLightReflex(OD) − CorneaLightReflex(OS)| ≥ threshold → Outside Range

| Gaze Component | Default Threshold (degrees, all ages) |
|----------------|--------------------------------------|
| Vertical | 8° |
| Nasal | 5° |
| Temporal | 8° |
| Asymmetry | 8° |

---

## Connectivity & Data Requirements

| Req | Requirement |
|-----|-------------|
| 40 | WLAN port (IEEE 802.11 a/b/g/n) for exam data transfer and printing |
| 41 | USB 2.0 port for data transfer and software upgrades |
| 26–39 | Report patient name (20 chars), DOB, gender, ID (30 chars), all measurements in display and printed form |
| 33–39 | Spherical Equivalent, Sph, Cyl, Axis, Gaze, IPD, Pupil Size reported per eye |

---

## Physical & Environmental Requirements

| Req | Requirement |
|-----|-------------|
| 43 | Design life: 5 years (1,450–22,917 exam cycles/year; 1,250–2,000 hours/year) |
| 44 | Operating: 10–40°C, 30–95% RH (non-condensing), 800–1060 hPa |
| 45 | Storage: −10–55°C, 10–95% RH (non-condensing), 700–1060 hPa |
| 46 | Shelf life: 5 years without operational degradation |
| 47 | Battery operation: ≥4 hours without external power or data storage |
| 48 | Weight: ≤2.5 lbs (handheld form factor) |

---

## Source Code Connections

### Referral / Threshold Logic
- **`vsd-src/libvsd-referral/`** — Implements the referral decision engine
  - `criteria.h` — `CriteriaList`, threshold definitions per condition per age range
  - `ReferralTestCase.h` — Unit test cases for each referral scenario
  - `ReferralTestData` — Constructs test vectors from exam results + expected pass/fail

### Measurement Results
- **`vsd-src/libvsd-examsys/`** — `ExamSysResults` struct holds Sph/Cyl/Axis/Gaze/Pupil/IPD per eye
- **`vsd-src/libvsd-refractive/`, `libvsd-refractive2/`, `libvsd-refractive3/`** — Compute Sph/Cyl/Axis from raw meridional responses (see theory-of-operation.md for math)
- **`vsd-src/pgvGaze/`** — Computes gaze/fixation axis (corneal reflex vs. pupil center)
- **`vsd-src/libvsd-cp/`** — Computes pupil size and IPD from circle-fitted pupil data

### Display & Reporting
- **`vsd-src/vsdgui/`** — Qt GUI renders results per eye; applies Within/Outside Range colouring
- **`vsd-src/vsd-results/`** — Exam results persistence and formatting
- **`vsd-src/vsd-printmgr/`** — CUPS-based print manager (`VsdPMJob`, `VsdPMPrintDriver`) for printed reports
- **`vsd-src/vsd-websvc/`** — REST API (`SpotWSvsdguiMonitor`) exposes results to external systems via WLAN; handles CSV export

### Configuration / User Settings
- **`vsd-src/libvsd-cfgstore/VsdSettings.h`** — Persists user-configurable thresholds; `VsdConfig.h` reads/writes settings to NAND/SD storage
- Default thresholds above are software defaults; user can override via GUI settings → `ConfigIni` on NAND/SD

---

## Key Document Cross-References
| Document | DIR | Notes |
|----------|-----|-------|
| DID (Design Input) | 60064652 Rev T | Root requirements; all measurement specs trace here |
| SRS (System Requirements) | 60064749 Rev Y | Full software requirements derived from DID |
| RAS (Risk Assessment) | 60065235 | Risk-based justification for many threshold values |
| Clinical Evaluation Report | 60067638 | Clinical validation of measurement accuracy claims |
| SADS | 60064690 | Architecture mapping requirements → components |
