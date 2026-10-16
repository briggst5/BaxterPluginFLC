# VS100CR Persistent Storage Design

> Source: SDS 60093088 "SDS, VS100 Persistent Storage" (Rev D or later)
> Author: Baxter / Welch Allyn Engineering

---

## Overview

The VS100CR has two physical storage media:
- **NAND Flash** — on-board flash; stores software image, manufacturing config, user settings
- **SD Card** — removable; stores user exam data (patient records, exam results, spot files)

Applications access all storage through a symbolic link at `/data` → SD card mount, and through explicit mount-point constants defined in `VsdFilePaths`.

---

## Storage Layout

### Mount Points

| Constant | Path | Medium | Contents |
|----------|------|--------|----------|
| `VsdFiles::NandConfig` | `/mnt/nandconfig` | NAND | Manufacturing config only |
| `VsdFiles::NandData` | `/mnt/nanddata` | NAND | User configuration files |
| `VsdFiles::SdData` | `/mnt/sddata` | SD card | User exam data |
| `VsdFiles::Data` | `/data` | symlink → SdData | Canonical data root |
| `VsdFiles::DataNormal` | `/data/normal` | SD card | Normal-mode data partition |
| `VsdFiles::DataSafe` | `/data/safe` | SD card | Safe-mode fallback partition |

### Data Categories

| Category | Medium | Description |
|----------|--------|-------------|
| Manufacturing Data | NAND | Serial number, calibration results, hardware key, mfg INI |
| User Settings | NAND | User-configurable options (language, printing, thresholds, auto-off) |
| Licensing | NAND | Device-specific license files `spot-<serial>.lic` / `.reg` |
| User Data | SD card | Patient records, exam results, spot files |
| Logging / Debug | SD card | Debug and diagnostic INI files |
| Encryption Secrets | NAND | AES keys used by `OpenSslAes` for data-at-rest encryption |
| Network Config | NAND/rootfs | Lighttpd, wpa_supplicant, systemd-networkd configs |

---

## Key Files in `libvsd-cfgstore/`

All storage access goes through `libvsd-cfgstore`. The file paths are centralised in `VsdFilePaths`:

### Manufacturing Files (NAND)
| Constant | File |
|----------|------|
| `VsdFiles::SerialIni` | Serial number record |
| `VsdFiles::MfgIni` | Manufacturing calibration settings |
| `VsdFiles::MfgResultsIni` | Pass/fail results from mfg test runs |
| `VsdFiles::MfgCfgDir` | Directory for all mfg files |
| `VsdFiles::MfgReportDir` | Mfg test report files (also on NAND for colocation) |

### License Files (NAND)
- Path format: `<LicenseCfgDir>/spot-<serial>.lic` and `.reg`
- Managed by `VsdLicensing.h` / `VsdLicenseFile.h`
- Device-specific; generated during manufacturing by the MFG SW suite
- Hardware key validated via `VsdHardwareKey.h` to bind license to device

### User Config Files (NAND)
| Constant | File | Purpose |
|----------|------|---------|
| `VsdFiles::ConfigIni` | `config.ini` | General user settings |
| `VsdFiles::SecurityIni` | `security.ini` | Security/access control settings |
| `VsdFiles::PrintersIni` | `printers.ini` | CUPS printer configuration |
| `VsdFiles::AutoOffIni` | `autooff.ini` | Auto-power-off timing |
| `VsdFiles::CriteriaCsvFilePath` | `criteria.csv` | User-configurable referral thresholds |

### Exam / User Data Files (SD card)
| Constant | File | Purpose |
|----------|------|---------|
| `VsdFiles::GazeValuesIni` | Debug/test use | Gaze result values |
| `VsdFiles::DebugIni` | `debug.ini` | Debug settings |
| `VsdFiles::PpiIni` | `ppi.ini` | Pixels-per-inch calibration data |
| `VsdFiles::VsdFocusIni` | `vsd-focus.ini` | Focus calibration data |

### Network/Service Config (rootfs/NAND)
| Constant | File |
|----------|------|
| `VsdFiles::WpaSupplicantConfFile` | Wi-Fi credentials |
| `VsdFiles::LighttpdConfFile` / `LighttpdWSConfFile` | Web server config (with / without WebSocket) |
| `VsdFiles::NetworkdConfFile` / `ResolveConfFile` | systemd-networkd and DNS |
| `VsdFiles::SpotVersionFile` | Installed software version |

---

## Key Classes in `libvsd-cfgstore/`

| Class | File | Purpose |
|-------|------|---------|
| `VsdConfig` | `VsdConfig.h` | Central configuration access; wraps INI read/write |
| `VsdSettings` | `VsdSettings.h` | User-configurable settings (wrappers over ConfigIni) |
| `VsdFilePaths` | `VsdFilePaths.h` | All path constants; single source of truth for file locations |
| `VsdLicensing` | `VsdLicensing.h` | License validation and feature-flag management |
| `VsdLicenseFile` | `VsdLicenseFile.h` | License file parsing |
| `VsdHardwareKey` | `VsdHardwareKey.h` | Reads device-unique hardware identifier used in license binding |
| `OpenSslAes` | `OpenSslAes.h` | AES-256 encryption/decryption of sensitive data at rest |
| `SettingsMfg` | `SettingsMfg.h` | Manufacturing-specific settings (read/write to MfgIni) |
| `MfgResultsIni` | `MfgResultsIni.h` | Read/write manufacturing test pass/fail results |
| `InitMicroSD` | `InitMicroSD.cpp` | Initialization and format of micro SD card |

---

## Data Migration

### Legacy System Migration (pre-3.1.01.00)
Devices upgrading from very old firmware (PediaVision-era) used a different persistent memory layout. Migration logic converts old-format files to the NAND/SD split layout on first boot after upgrade.

### Migration from pre-3.1.03.00
An additional migration step handles settings changes introduced in 3.1.03.00 (exact fields TBD from source).

### Factory Reset
- Implemented in `PowerWorker::factoryReset()` → `eraseUserData()`
- Deletes all user data from SD card (`/data/normal/` contents)
- Preserves manufacturing data (NAND config) and license files
- Restores user settings to defaults (wipes `NandData` user INI files)
- D-Bus signal: `Power::factoryReset()` → `factoryreset()` slot triggers `PowerWorker`

---

## Fault Handling

- Storage errors during write → logged to `DebugIni`; device continues operating
- SD card missing or corrupt → exam data cannot be saved; GUI warns user
- `DataSafe` path used as fallback if `DataNormal` is unavailable (mirrors safe/main image pattern from boot)
- `RecoveredDir` — directory for files recovered from a previous failed operation

---

## Spot File Management

Spot files (exam results) are stored on the SD card under `SdData`. The spot file lifecycle:

1. **Created** during exam execution by `libvsd-examsys`
2. **Indexed** by `vsd-results` / the GUI results list
3. **Exported** via `vsd-websvc` (REST API, CSV) or `vsd-printmgr` (CUPS print)
4. **Deleted** by user action via GUI → `SpotWSvsdguiMonitor::clearResult()` / `clearResults()`

`VsdFiles::CriteriaCsvFilePath` defines the criteria file consumed by `libvsd-referral` for referral threshold decisions.

---

## Security Considerations (OWASP / IEC 62304)

- AES encryption of sensitive data via `OpenSslAes` (OpenSSL backend)
- License files are device-bound via hardware key → prevents license transfer between devices
- `SecurityIni` controls access control settings (e.g., admin PIN, remote access enable/disable)
- Web server credentials: `LighttpdUserFile` and `LighttpdWSAuthConfFile`
- Factory reset wipes exam data but preserves calibration — cannot be used to bypass licensing

---

## Source Cross-References

| Concern | Module |
|---------|--------|
| Central config access | `vsd-src/libvsd-cfgstore/VsdConfig.h` |
| All file paths | `vsd-src/libvsd-cfgstore/VsdFilePaths.h` |
| Encryption | `vsd-src/libvsd-cfgstore/OpenSslAes.h` |
| Licensing | `vsd-src/libvsd-cfgstore/VsdLicensing.h`, `VsdLicenseFile.h`, `VsdHardwareKey.h` |
| Mfg settings | `vsd-src/libvsd-cfgstore/SettingsMfg.h`, `MfgResultsIni.h` |
| Factory reset / power-off | `vsd-src/vsd-power/inc/powerworker.h` |
| SD card init | `vsd-src/libvsd-cfgstore/InitMicroSD.cpp` |
| Referral thresholds (criteria) | `vsd-src/libvsd-referral/criteria.h` |
| Results (spot files) | `vsd-src/vsd-results/`, `vsd-src/libvsd-examsys/` |
| Web export / CSV | `vsd-src/vsd-websvc/` |
