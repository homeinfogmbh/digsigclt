"""Check mount points."""

from pathlib import Path


__all__ = ['boot_mounted']


EFI_PARTITION = Path('/dev/disk/by-label/EFI')
BOOT = Path('/boot')


def boot_mounted() -> bool:
    """Checks whether the boot partition is mounted.
    Also return True if not applicable.
    """

    return not efi_not_mounted_as_boot()


def efi_not_mounted_as_boot() -> bool:
    """Return True iff there is an EFI partition
    to be mounted on /boot, but it is not.
    """

    return EFI_PARTITION.is_block_device() and not BOOT.is_mount()
