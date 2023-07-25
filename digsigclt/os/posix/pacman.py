"""Pacman related commands."""

from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from digsigclt.exceptions import PackageManagerActive
from digsigclt.os.common import command
from digsigclt.os.posix.common import sudo


__all__ = ["is_running", "pacman", "unlock", "package_version"]


@command(as_bool=True)
def is_running() -> list[str]:
    """Check if pacman is running."""

    return ["/usr/bin/pidof", "pacman"]


@command()
def unlock() -> list[str]:
    """Unlock the package manager."""

    if is_running():
        raise PackageManagerActive()

    return sudo("/usr/bin/rm", "-f", "/var/lib/pacman/db.lck")


def pacman(*args: str) -> CompletedProcess:
    """Run pacman."""

    return run(
        ["/usr/bin/pacman", *args], check=True, text=True, stderr=PIPE, stdout=PIPE
    )


def package_version(package: str) -> str | None:
    """Return the package version."""

    try:
        result = pacman("-Q", package)
    except CalledProcessError:
        return None

    return result.stdout.strip().split()[1]
