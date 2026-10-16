# VS100CR Manufacturing Software Suite

> Source: SRS 60096492 "SRS, VS100CR MFG SW Suite" (Rev E), Author: Eric J. Laurin

---

## Overview

The **Manufacturing Software Suite** automates portions of the VS100CR production process:
- Hardware calibration
- Hardware functional testing
- License key generation
- Printed test result records

It runs **on the VS100CR device itself** using a separate manufacturing software image loaded from SD card. It is **not customer-accessible** and is intended only for trained Welch Allyn / Baxter personnel (service and manufacturing staff).

---

## High-Level Requirements

| Req | Requirement |
|-----|-------------|
| MFG-1 | Automate calibration of VS100CR hardware |
| MFG-2 | Automate hardware functional tests |
| MFG-3 | Generate license key file(s) for each device |
| MFG-4 | Produce printed records of test results |
| MFG-5 | Run on the VS100CR device (not a separate host PC) |
| MFG-6 | Not accessible to end customers |
| MFG-7 | Intended for trained personnel only (manufacturing and service) |

---

## Manufacturing Flow

```
Factory:
  1. Boot VS100CR from SD card (SD card boot → NAND flash)
  2. NAND programmed with manufacturing SW image (not production image)
  3. Run Manufacturing SW Suite (vsd-mfg-test)
     ├── Hardware functional tests (LEDs, camera, buttons, Wi-Fi, battery, etc.)
     ├── Calibration (exposure, focus metric, camera)
     ├── License key generation (bound to device hardware key)
     └── Print / record results to MfgResultsIni + printed report
  4. If all tests pass → install production software image
  5. Run production smoke test
```

After mfg SW runs, device is calibrated and licensed. If SD card install erased NAND, the mfg test suite must run again to restore calibration and license.

---

## Hardware Tests Performed

Based on SRS and source (`vsd-mfg-test/inc/`):

| Test | Description |
|------|-------------|
| LED Test | Verifies NIR LED board illumination (all 23 LEDs sequenced) |
| Camera Test | Verifies image capture pipeline |
| Battery Discharge Test | `BatteryDischargeTest.h` — validates battery capacity and discharge rate |
| Power Button Test | `TestWndPowerButton.h` — GPIO power button response |
| Display Test | Verifies LCD display functionality |
| Wi-Fi Test | Tests WLAN connectivity |
| Serial / ID | Reads and validates device serial number from hardware |
| Touch Screen Calibration | `VsdTSCalibrate` (via `vsd-src/libvsd-tscalibrate/`) |
| Focus Calibration | Verifies autofocus mechanism; writes `PpiIni` and `VsdFocusIni` |

---

## Calibration Outputs

Calibration results are written to persistent storage (NAND) via `libvsd-cfgstore`:

| File | Content | Constant |
|------|---------|---------|
| `serial.ini` | Device serial number, hardware key | `VsdFiles::SerialIni` |
| `mfg.ini` | Calibration parameters (exposure tables, focus settings) | `VsdFiles::MfgIni` |
| `mfg-results.ini` | Pass/fail for each test step | `VsdFiles::MfgResultsIni` |
| `ppi.ini` | Pixels-per-inch calibration (camera geometry) | `VsdFiles::PpiIni` |
| `vsd-focus.ini` | Focus calibration data | `VsdFiles::VsdFocusIni` |
| `spot-<serial>.lic` + `.reg` | License files bound to hardware key | `VsdFiles::LicenseCfgDir` |

---

## License Key Generation

- License file is **device-specific**: bound to a unique hardware key read from `VsdHardwareKey`
- Two files created: `.lic` (feature entitlements) and `.reg` (registration/device binding)
- Enables the exam system and optional features (e.g., China-specific mode via "Chinese License Key File")
- `VsdLicensing.h` / `VsdLicenseFile.h` implement license validation at runtime
- If the NAND is re-flashed via SD card, the device loses its license → must regenerate via mfg test

---

## Master SD Card

- A **Master Micro SD Card** is pre-loaded with the manufacturing software image
- Distributed to manufacturing and service personnel
- Device boots from this SD card to run mfg tests (see sw-lifecycle-and-upgrade.md for SD boot details)
- After mfg tests pass, the production SD card (non-bootable, for user data) is installed

---

## Source Code Connections

| Concern | Source module |
|---------|--------------|
| Manufacturing test application | `vsd-src/vsd-mfg-test/` |
| Test UI / main window | `vsd-src/vsd-mfg-test/inc/mainwindow.h` |
| Battery discharge test | `vsd-src/vsd-mfg-test/inc/BatteryDischargeTest.h` |
| Power button test | `vsd-src/vsd-mfg-test/inc/TestWndPowerButton.h` |
| Manufacturing constants | `vsd-src/vsd-mfg-test/inc/ConstantsMfg.h` |
| Calibration storage write | `vsd-src/libvsd-cfgstore/SettingsMfg.h`, `MfgResultsIni.h` |
| License generation | `vsd-src/libvsd-cfgstore/VsdLicensing.h`, `VsdLicenseFile.h` |
| Hardware key read | `vsd-src/libvsd-cfgstore/VsdHardwareKey.h` |
| Touch screen calibration | `vsd-src/libvsd-tscalibrate/` |
| File paths | `vsd-src/libvsd-cfgstore/VsdFilePaths.h` (MfgIni, SerialIni, MfgResultsIni, etc.) |
| Check5G (post-mfg SW verification) | `vsd-src/libvsd-cfgstore/Check5G.cpp` |
| ARX hardening (mfg binary) | `vsd-src/vsd-mfg-test/arxan/` (same EnsureIT pattern as production) |

---

## Manufacturing Firmware (IR LED Board)

The IR LED board firmware (separate from the application) is also managed during manufacturing:
- Firmware flashed during production
- Controls NIR LED sequencing synchronized with camera (23 LEDs, 850 nm)
- Version tracked in mfg records
- Not part of field software upgrade

---

## Cross-References

| Document | DIR | Notes |
|----------|-----|-------|
| DID | 60064652 | Requirements for measurement accuracy verified during mfg calibration |
| SRS VS100CR | 60064749 | Parent requirements for mfg SW requirements traceability |
| MFG Test Spec | 60072221 | Detailed test specifications for each mfg test step |
| SW Install & Upgrade SDS | 60096522 | Boot procedure for loading mfg SW via SD card |
| Persistent Storage SDS | 60093088 | Storage layout for mfg data (NAND) |
