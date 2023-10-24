---
name: Bug report
about: Your detailed bug reports are pivotal in elevating this project's quality.
  Your expertise in identifying issues is deeply valued and appreciated.
title: "[ISSUE] Problem Encountered"
labels: bug
assignees: franckferman

---

## Problem Summary
_Provide a clear and concise summary of the encountered issue._

## Steps to Reproduce
Provide a step-by-step description on how to reproduce the anomaly:

1. Command initiated: `...`
2. During the process: `....`
3. Observed issue: `....`
4. Output/response anomaly: `...`

## Expected Outcome
_Describe the anticipated result after executing the provided steps._

## Visual Evidence
If possible, attach screenshots to support your description.

## Technical Details

### Operating System

- **Linux:** [e.g. Linux root 4.19.0-6-amd64 #1 SMP Debian 4.19.67-2+deb10u1 (2019-09-20) x86_64 GNU/Linux]
  *Retrieval:* `uname -a`

- **Windows:** [e.g. Microsoft Windows 10 Pro DevBox 10.0.15063 Multiprocessor Free 64-bit]
  *Retrieval:* 
  ```powershell
  $Properties = 'Caption', 'CSName', 'Version', 'BuildType', 'OSArchitecture'
  Get-CimInstance Win32_OperatingSystem | Select-Object $Properties | Format-Table -AutoSize
  ```

### Software Versions

- **Python**: [e.g. Python 3.11.4]
  *Retrieval:* `python3 -V`

- **Exiftool**: [e.g. 12.56]
  *Retrieval:* `exiftool -ver`

- **MetaDetective**: [e.g. 1.0.7]

### Docker (if used)

- **Image Version**: [e.g. "1.0.1"]

## Additional Information

Provide any other pertinent details or context regarding the issue.
