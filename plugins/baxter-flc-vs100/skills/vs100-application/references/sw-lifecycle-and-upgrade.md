# VS100CR Software Lifecycle, Installation & Upgrade

> Sources:
> - SDS 60096522 "SDS, VS100CR SW Installation and Upgrade" (Rev D), Author: Lukasz Wojdasiewicz
> - SDP 60133184 "SDP, VS100 Kernel Updates" (Rev E), Author: Eric J. Laurin
> - SDP 60133184 "SDP, VS100 3.3.0.x Battery Life" (Rev H)

---

## Development Lifecycle (IEC 62304 / SOP-0321)

The VS100CR software follows the **Baxter Continuing Design Change Process** (SOP-20213) anchored to the **Software Development Process** (SOP-0321).

### Safety Classification
The VS100CR software is classified as **IEC 62304 Class B** (non-life-threatening injury possible). This drives:
- Requirements traceability from SRS → design → test
- Formal SFMEA (Software Failure Modes and Effects Analysis) and/or SHA (Software Hazard Analysis)
- Security Risk Assessment (SRA) reviewed per public CVE feeds
- OTS/SOUP anomaly review for all third-party components

### Roles
| Role | Responsibility |
|------|---------------|
| Software Engineering (Project Lead) | Technical direction, SDP maintenance, tool selection |
| System Test | System-level verification, independent of developers |
| Design Assurance | Overall verification authority; verifies testers are independent |
| Project Management | Issue resolution, milestone tracking in ADO |

### Milestones (from SOP-0321)
Configuration baselines established at each milestone: SRS → SADS → SDS → implementation → unit test → integration → system verification → design transfer.

---

## Configuration Management

- **Source control**: Git, repositories `vsd-base` and `vsd-src` (separate Git repos, composed via repo manifest)
- **CI/CD platform**: Azure DevOps (ADO) organization **"FLC-Embedded"** (`vsdbuild/`)
- **Issue tracking**: Azure DevOps work items (ADO replaces JIRA in some projects)
- **Requirements traceability**: Requirements Traceability Matrix (RTM) per SOP-0348: system req → software req → design → test

### Repository Structure
```
vs100-coding-agent/               ← repo workspace root
  vs100-application-workspace/    ← vsd-base + vsd-src (application code)
  vs100-dev-build/                ← Yocto/OE build environment (sources/ layers)
  vsdbuild/                       ← Azure DevOps pipeline YAMLs + workspace setup
```

---

## Tools & Methodologies

### Development Tools (per SDP Appendix B)
| Tool | Purpose |
|------|---------|
| Git | Version control for all source |
| CMake 3.20+ | Build system (see `vs100-application` skill for flags) |
| Azure DevOps | CI/CD, work items, test management |
| LLVM/Clang | Cross-compilation toolchain (ARM target) |
| Fortify SAST | Static Application Security Testing; required CI gate |
| Digital.ai App Hardening (EnsureIT/ARX) | Binary hardening for security; see ensureit-app-hardening.md |
| Wind River FlexOS Linux (from Siemens) | BSP + OTS/SOUP Linux OS (replaces Poky baseline on newer HW) |
| BitBake / Yocto | Image build system (Poky Dunfell for VS100CR) |
| OpenSSL | Encryption library used in `OpenSslAes.h` (storage encryption) |

### OTS / SOUP Management
- OTS open-source packages provided through **Wind River FlexOS Linux** (Siemens)
- Siemens reviews OTS anomaly lists; findings evaluated against SFMEA/SHA
- A SOW governs BSP development/verification deliverables; maintenance contract covers ongoing support
- Internal OTS: Qt (GUI), CUPS (printing), Lighttpd (web server), D-Bus, OpenSSL

### Coding Standard
- Internal: **80025811 — Embedded Software Coding Standard**
- C++20 (application), CMake for build
- Each algorithm or complex sequence must be commented

---

## Boot Process

The microcontroller (TI eSOM3730) uses GPIO pins to determine boot source: **SD card first, then NAND flash**.

### Boot Sequence
```
ROM code
  → loads MLO (first-stage bootloader) from SD or NAND (mtd0)
    → MLO initializes hardware
      → loads U-Boot (second-stage bootloader) from same source (mtd1)
        → U-Boot checks boot type:
            SD card: runs install script (factory use only)
            NAND: loads main or safe kernel → Linux → application
```

### Booting from SD Card (Factory Installation)
Used **only during manufacturing** to flash NAND:
1. SD card contains MLO, U-Boot, kernel (x2), main rootfs, safe image, metadata
2. U-Boot executes SD install script: erases NAND, programs all partitions
3. On completion: asserts GPIO to power off device
4. Operator removes SD, installs final (non-bootable) SD card
5. Next power-on boots from freshly programmed NAND into manufacturing test

### Booting from NAND (Normal Operation)
- U-Boot selects **main kernel** (mtd4) + **rootfs** (mtd6) for normal operation
- Selects **safe image** (mtd5) when entering software upgrade mode

---

## NAND Flash Partition Layout

11 MTD partitions on internal NAND (total ~1 GB):

| Partition | Offset Start | Size | Name | Description |
|-----------|-------------|------|------|-------------|
| mtd0 | 0x00000000 | 0.5 MB | MLO | First-stage bootloader |
| mtd1 | 0x00080000 | 4.0 MB | U-Boot | Second-stage bootloader |
| mtd2 | 0x00480000 | 1.0 MB | U-Boot Env | Bootloader environment variables |
| mtd3 | 0x00580000 | 10.0 MB | FlexOS extra | Linux configuration data |
| mtd4 | 0x00F80000 | 100.0 MB | Kernel | Main Linux kernel (normal operations) |
| mtd5 | 0x07380000 | 100.0 MB | Safe image | Linux kernel+initramfs used during SW upgrade |
| mtd6 | 0x0D780000 | 575.0 MB | Rootfs | Main root filesystem (GUI, exam, all functionality) |
| mtd7 | 0x31680000 | 200.0 MB | Data | Configuration settings and temporary data |

**Main rootfs** (mtd6): Full GUI application, exam system, printing, results, web service.  
**Safe rootfs** (embedded in mtd5): Minimal UI showing upgrade progress; handles upgrade of mtd4+mtd6 only.

---

## Software Installation (SD Card Image)

### SD Card Image Structure
The build generates a WIC-format image with two partitions:

**Partition 1 (VFAT, 128 MB) — `boot`:**
| File | Description |
|------|-------------|
| `MLO` | First-stage bootloader |
| `u-boot.img` | Second-stage bootloader |
| `fitImage` | Main Linux kernel (normal operations) |
| `fitImage-golden` | Safe Linux image (kernel + initramfs, used for upgrade) |

**Partition 2 (Ext4, 1 GB) — `root`:**
| File | Description |
|------|-------------|
| `rootfs` | Main Linux root filesystem |

### Build Process (Yocto)
1. All SD card files generated by `bitbake` (see `vs100-image-build` skill)
2. WIC image created: VFAT boot partition (128 MB) + Ext4 root partition (1 GB)
3. Image compressed for distribution

### Installing from SD Card
- Plug SD into daughter-board slot while device is **powered off**
- Power on → software installs automatically
- **Note**: Case must be disassembled for SD access → not for field upgrades
- Post-install: device is uncalibrated and unlicensed → must run full mfg test suite

---

## Software Upgrade (Field Upgrade via USB)

### Upgrade Binary Image Contents
The `.bin` upgrade file delivered via USB thumb drive contains:
- First-stage bootloader (current + legacy versions for rollback safety)
- U-Boot bootloader (code + environment settings)
- Linux kernel
- Main root filesystem
- Safe Linux image
- Software description file (SHA-256 checksums for each component)
- Digital signature of the software description file (integrity verification)

### Upgrade Procedure
1. User inserts USB thumb drive with upgrade binary into VS100CR
2. GUI detects upgrade binary; user initiates upgrade
3. Device reboots into **safe image** (mtd5)
4. Safe rootfs minimal UI shows progress; writes new kernel (mtd4) and rootfs (mtd6)
5. SHA-256 checksums verified before and after write
6. Device reboots into new **main kernel + rootfs**
7. Data migration runs if required (storage format changes between versions)

### HW/SW Compatibility
- Compatibility table maintained in DIR 60105481
- SD card image generation records metadata used to validate compatibility during subsequent upgrades
- HW Rev D: requires SW ≥ 3.0.04.10

---

## IR LED Board Firmware

The **only firmware written and controlled by Baxter engineering** (separate from device software):
- Runs on the IR LED board (not eSOM3730)
- Controls sequencing of 23 NIR LEDs synchronized with camera sensor
- Version is tracked; upgrade path differs from main SW upgrade
- All other peripheral firmware (wireless module, etc.) is supplier-maintained; wireless module firmware is field-upgradable

---

## Software Architecture Groupings

Three major groupings on the eSOM3730 main board (from SDP block diagram):
1. **OSS** (green): Open-Source Software from Wind River FlexOS / OE layers
2. **Interface/utility libraries** (blue): `vsd-base/` — shared threading, D-Bus, platform utilities
3. **Application workflows** (orange): `vsd-src/` — all product-specific modules (pupil, refraction, GUI, print, web, etc.)

---

## Battery Life Project (SDP 60133184 Rev H)

The Battery Life SDP covers SW changes in VS100 3.3.0.x to improve battery life:
- **LCD Flicker project**: Addresses LCD screen flicker (CR 26372); includes display power management changes
- **Siemens → Wind River transition**: OTS/BSP provider rebranded; SDLC documents updated throughout
- Key modules affected: `vsd-power/` (backlight levels, auto-off), `libvsd-power-dbus/`
- Power constants: `normalLevel = 8`, `dimLevel = 2`, `darkLevel = 0` (0–10 scale) — in `vsd-power.h`
- D-Bus signals: `dimBacklightsignal`, `darkBacklightsignal`, `powerOffSystem`, `rebootSystem`, `factoryReset`

---

## Source Code Connections

| Concern | Source |
|---------|--------|
| Boot / upgrade scripts | `vs100-dev-build/` Yocto recipes, `meta-baxter-bsp/` |
| Power management application | `vsd-src/vsd-power/` (`Power`, `PowerWorker` classes) |
| Power D-Bus interface | `vsd-src/libvsd-power-dbus/` |
| Factory reset / data wipe | `vsd-src/vsd-power/inc/powerworker.h` — `factoryReset()`, `eraseUserData()` |
| Device revision detection | `vsd-src/devicerevision/` |
| Software version file | `VsdFiles::SpotVersionFile` in `libvsd-cfgstore/VsdFilePaths.h` |
| CI pipelines (build + EnsureIT) | `vsdbuild/dev/` and `vsdbuild/3.2.00/` Azure DevOps YAMLs |
| Security hardening (build-time) | `vsd-src/arx/` GuardSpec + `vsd-src/libvsd-security/` (see ensureit-app-hardening.md) |
| Web service (remote connection) | `vsd-src/vsd-websvc/` (`SpotWSvsdguiMonitor`) |
