#!/usr/bin/env python3

""" Enumerate process capabilities from procfs, on Linux """

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Set

PROCFS = Path("/proc")

CAPABILITIES = {
    0  : 'CAP_CHOWN',
    1  : 'CAP_DAC_OVERRIDE',
    2  : 'CAP_DAC_READ_SEARCH',
    3  : 'CAP_FOWNER',
    4  : 'CAP_FSETID',
    5  : 'CAP_KILL',
    6  : 'CAP_SETGID',
    7  : 'CAP_SETUID',
    8  : 'CAP_SETPCAP',
    9  : 'CAP_LINUX_IMMUTABLE',
    10 : 'CAP_NET_BIND_SERVICE',
    11 : 'CAP_NET_BROADCAST',
    12 : 'CAP_NET_ADMIN',
    13 : 'CAP_NET_RAW',
    14 : 'CAP_IPC_LOCK',
    15 : 'CAP_IPC_OWNER',
    16 : 'CAP_SYS_MODULE',
    17 : 'CAP_SYS_RAWIO',
    18 : 'CAP_SYS_CHROOT',
    19 : 'CAP_SYS_PTRACE',
    20 : 'CAP_SYS_PACCT',
    21 : 'CAP_SYS_ADMIN',
    22 : 'CAP_SYS_BOOT',
    23 : 'CAP_SYS_NICE',
    24 : 'CAP_SYS_RESOURCE',
    25 : 'CAP_SYS_TIME',
    26 : 'CAP_SYS_TTY_CONFIG',
    27 : 'CAP_MKNOD',
    28 : 'CAP_LEASE',
    29 : 'CAP_AUDIT_WRITE',
    30 : 'CAP_AUDIT_CONTROL',
    31 : 'CAP_SETFCAP',
    32 : 'CAP_MAC_OVERRIDE',
    33 : 'CAP_MAC_ADMIN',
    34 : 'CAP_SYSLOG',
    35 : 'CAP_WAKE_ALARM',
    36 : 'CAP_BLOCK_SUSPEND',
    37 : 'CAP_AUDIT_READ',
}

FULLCAP = 0x3FFFFFFFFF
FULLCAP_SET = set(CAPABILITIES.values())

class CapsUnsupportedError(OSError):
    pass

class CapsProcessNotFoundError(KeyError):
    pass

@dataclass
class ProcessCapabilities:
    pid: int
    effective_caps: Set[str]
    unknown_effective_caps: Set[int]

def has_caps(pid: int, caps: set) -> bool:
    _caps = get_process_capabilities(pid)
    return _caps.effective_caps & caps == caps

def get_process_capabilities(pid: int) -> ProcessCapabilities:
    """ On Linux, return a set of all the capabilities the given PID has. The second return tuple
    item is a set of the hex values of all unknown capability values found. This set should be empty
    if this function is implemented correctly for the given kernel. As the list of caps may be
    expanded in the future, on some kernels, the second set may not be empty. """

    if not PROCFS.exists():
        raise CapsUnsupportedError("procfs not found at {PROCFS} -- require procfs at that location")

    status = PROCFS / str(pid) / "status"

    if not status.is_file():
        raise CapsProcessNotFoundError(f"{status} not found -- process may have terminated")

    effective_caps = set()
    unknown_effective_caps = set()

    with status.open("r") as FILE:
        for line in FILE:
            if line.startswith("CapEff"):
                caps_field = line[:-1].split(chr(0x09), 1)[-1]
                assert len(caps_field) > 0, "CapEff field in {status} in unexpected format: {caps}"
                caps = int(line[:-1].split(chr(0x09), 1)[-1], 16)

                if caps == FULLCAP:
                    effective_capabilities = FULLCAP_SET
                    break

                for i in range(0, 64, 1):
                    if ((caps >> i) & 0x1) == 1:
                        if capstr := CAPABILITIES.get(i, None):
                            effective_caps.add(capstr)
                        else:
                            unknown_effective_caps.add(i)

    return ProcessCapabilities(
            pid = pid,
            effective_caps = effective_caps,
            unknown_effective_caps = unknown_effective_caps,
    )
