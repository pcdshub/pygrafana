from collections import UserString
from pathlib import Path
from typing import Optional


class VersionProxy(UserString):
    """
    Version handling helper that pairs with setuptools-scm.

    This allows for pkg.__version__ to be dynamically retrieved on request by
    way of setuptools-scm.

    This deferred evaluation of the version until it is checked saves time on
    package import.

    This supports the following scenarios:

    1. A git checkout (.git exists)
    2. A git archive / a tarball release from GitHub that includes version
        information in .git_archival.txt.
    3. An existing _version.py generated by setuptools_scm
    4. A fallback in case none of the above match - resulting in a version of
        0.0.unknown
    """

    def __init__(self):
        self._version = None

    def _get_version(self) -> Optional[str]:
        # Checking for directory is faster than failing out of get_version
        here = Path(__file__).resolve()
        repo_root = here.parent.parent
        if (repo_root / ".git").exists() or (repo_root / ".git_archival.txt").exists():
            try:
                # Git checkout
                from setuptools_scm import get_version

                return get_version(root="..", relative_to=here)
            except (ImportError, LookupError):
                ...

        # Check this second because it can exist in a git repo if we've
        # done a build at least once.
        try:
            from ._version import version  # noqa: F401

            return version
        except ImportError:
            ...

        return None

    @property
    def data(self) -> str:
        # This is accessed by UserString to allow us to lazily fill in the
        # information
        if self._version is None:
            self._version = self._get_version() or "0.0.unknown"

        return self._version


__version__ = version = VersionProxy()