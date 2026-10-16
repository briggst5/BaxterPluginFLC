---
name: vs100-application
description: >
  Deep knowledge of the VS100 C++20 application codebase (Baxter). Use for: architecture questions,
  module relationships, feature implementation, CMake build system, cross-compilation, library APIs,
  IPC/D-Bus patterns, Qt GUI components, exam system workflows, configuration store, power management,
  refractive/spot algorithms, security, SNMP, web service, and repo manifest structure.
  Workspace root: vs100-application-workspace/
argument-hint: "Ask about a module, subsystem, or implementation detail."
---

# VS100 Application Codebase

## Workspace Layout

```
vs100-application-workspace/
├── CMakeLists.txt          # Top-level: project VS100 3.2.00, C++20, ARM cross-compile
├── vsd-base/               # Shared platform base (interfaces, common, threading)
│   ├── interfaces/         # Public headers shared across all modules
│   └── src/                # Platform-level common and thread utilities
├── vsd-src/                # All product modules and libraries
│   ├── lib*/               # Reusable shared libraries (see Module Map below)
│   ├── pgm*/               # Standalone executables
│   ├── vsd*/               # Top-level applications (GUI, power, printing, results, websvc)
│   └── scripts/            # Build and helper scripts
└── .vsdbuild/              # Workspace setup scripts and manifest manifests per revision
    └── workspace-setup.sh  # Entry point: requires workspace_path and revision args
```

## Module Map

| Directory | Type | Purpose |
|---|---|---|
| `vsd-base/` | Base | Shared interfaces, common utilities, threading primitives |
| `libexecuteprocess/` | Library | Child process execution helpers |
| `libstdinreader/` | Library | Asynchronous stdin reading |
| `libunixsignalhandlers/` | Library | POSIX signal handler registration |
| `libvsd-cfgstore/` | Library | Configuration store (persistent key-value) |
| `libvsd-cp/` | Library | Camera/capture pipeline; pupil and capture sub-modules |
| `libvsd-dbusmonitor/` | Library | D-Bus signal monitoring |
| `libvsd-examsys/` | Library | Exam system state machine and workflow |
| `libvsd-keyboardmanager/` | Library | Keyboard input management |
| `libvsd-power-dbus/` | Library | Power management D-Bus XML interfaces |
| `libvsd-referral/` | Library | Referral document handling |
| `libvsd-refractive/` | Library | Refractive measurement algorithm (v1) |
| `libvsd-refractive2/` | Library | Refractive measurement algorithm (v2) |
| `libvsd-refractive3/` | Library | Refractive measurement algorithm (v3) |
| `libvsd-security/` | Library | Security and access control |
| `libvsd-snmp/` | Library | SNMP agent integration |
| `libvsd-spotdialog/` | Library | Spot measurement dialog UI component |
| `libvsd-spotspinner/` | Library | Spot animation/spinner UI component |
| `libvsd-spotthread/` | Library | Spot measurement background thread |
| `libvsd-tscalibrate/` | Library | Touchscreen calibration |
| `arx/` | Module | EnsureIT ARX integration (optional, `ENABLE_ARX` flag) |
| `devicerevision/` | Module | Device hardware revision detection |
| `pgmPupil/` | Executable | Pupil measurement program |
| `pgvAnalysis/` | Executable | Analysis viewer |
| `pgvGaze/` | Executable | Gaze tracking program |
| `vsd-focus/` | Application | Focus subsystem |
| `vsd-mfg-test/` | Application | Manufacturing test (enabled via `MFG_BUILD` flag) |
| `vsd-power/` | Application | Power management daemon |
| `vsd-printmgr/` | Application | Print manager |
| `vsd-results/` | Application | Results viewer |
| `vsd-websvc/` | Application | Embedded web service |
| `vsdgui/` | Application | Main Qt GUI application |

## Build System

- **Generator**: CMake 3.20+ (top-level), 3.22.1+ (vsd-src)
- **Standard**: C++20
- **Compiler flags**: `-Wall -Werror -Wextra -Wpedantic`
- **Cross-compile**: `CROSS_COMPILE` env var sets the toolchain prefix; output goes to `$BUILD_DIR/${CROSS_COMPILE}lib` and `${CROSS_COMPILE}bin`
- **Key CMake options**:
  - `BUILD_GUI` (default ON) — enables Qt GUI applications
  - `MFG_BUILD` (default OFF) — manufacturing test build; disables `BUILD_GUI`
  - `ENABLE_ARX` (default OFF) — enables EnsureIT ARX module
- **Fortify**: Static analysis via `FORTIFY_INCLUDES` env var; `Fortify_CI` pipeline exists alongside main CI

## Repo Manifest

The workspace is managed with the `repo` tool.

- Manifest: `.repo/manifest.xml`
- Init/sync via `workspace-setup.sh workspace_path revision` (must be sourced with `.`)
- Revisions: `dev`, `3.2.00` (controlled by `vsdbuild/` folder names)

## How to Answer Questions

1. **Architecture / relationships**: Map the question to modules in the table above. Read the relevant `CMakeLists.txt` to confirm `target_link_libraries` and inter-module dependencies.
2. **Feature implementation**: Navigate to the owning module directory. Read its `inc/` or top-level headers first, then `src/` implementation files.
3. **Build configuration**: Check top-level `CMakeLists.txt` and `vsd-src/CMakeLists.txt` for flags, options, and include paths.
4. **Interface contracts**: Public APIs live under `vsd-base/interfaces/`. Check there before reading implementation.
5. **D-Bus interfaces**: XML definitions are co-located with their owning library (e.g. `libvsd-power-dbus/xml/`).
6. **Always cite the file** (relative to `vs100-application-workspace/`) when making a claim about implementation.

## Reference Documents

The following reference files are embedded in this skill and always available:

| Reference | Covers |
|---|---|
| [Theory of Operation](./references/theory-of-operation.md) | Device purpose, NIR LED stimuli, pupil acquisition algorithm, refractive error analysis (sphere/cylinder/axis), fixation axis, examination phases |
| [EnsureIT / App Hardening](./references/ensureit-app-hardening.md) | GuardSpec model, guard types, protection workflow, ARX namespace, VS100 source integration, CI pipeline variants |
| [Requirements & Referral Logic](./references/requirements-and-referral-logic.md) | Clinical measurement ranges/accuracy (DID Req 1–12), age-stratified referral thresholds (myopia, hyperopia, astigmatism, anisometropia, anisocoria, strabismus), connectivity/physical requirements, connections to `libvsd-referral/` |
| [Persistent Storage Design](./references/persistent-storage-design.md) | NAND/SD card partition roles, all `VsdFilePaths` constants, `libvsd-cfgstore` class map (VsdConfig, VsdSettings, VsdLicensing, OpenSslAes), data categories, migration, factory reset |
| [SW Lifecycle & Upgrade](./references/sw-lifecycle-and-upgrade.md) | IEC 62304 Class B lifecycle, ADO CI/CD, tool chain, boot process (MLO→U-Boot→kernel), NAND partition table, SD card image structure, field upgrade via USB, IR LED firmware, battery life SDP |
| [Manufacturing SW Suite](./references/mfg-sw-suite.md) | `vsd-mfg-test/` application, hardware test sequence, calibration outputs, license key generation, master SD card workflow, connections to `libvsd-cfgstore/SettingsMfg`, `VsdLicensing`, `VsdHardwareKey` |

### When to load which reference

| Question topic | Load first |
|----------------|-----------|
| How VS100 measures refraction / pupil algorithm / exam phases | [Theory of Operation](./references/theory-of-operation.md) |
| Measurement accuracy limits / referral pass-fail thresholds | [Requirements & Referral Logic](./references/requirements-and-referral-logic.md) |
| Where data is stored / `libvsd-cfgstore` API / VsdFilePaths / factory reset | [Persistent Storage Design](./references/persistent-storage-design.md) |
| Boot sequence / NAND layout / SW upgrade / SD card install / build pipeline | [SW Lifecycle & Upgrade](./references/sw-lifecycle-and-upgrade.md) |
| Manufacturing tests / calibration / license key generation / `vsd-mfg-test` | [Manufacturing SW Suite](./references/mfg-sw-suite.md) |
| EnsureIT / ARX / tamper protection / `libvsd-security` | [EnsureIT / App Hardening](./references/ensureit-app-hardening.md) |

## Search Strategy

When asked about a subsystem, search in this order:
1. Relevant reference document (table above) — for design intent, requirements, system-level behavior
2. `vsd-base/interfaces/` — shared header contracts
3. `vsd-src/<matching-module>/inc/` or `vsd-src/<matching-module>/` headers
4. `vsd-src/<matching-module>/src/` — implementation
5. `vsd-src/CMakeLists.txt` — wiring and compile-time flags
6. `vsdgui/` — if the question involves the user interface
