import subprocess
from collections.abc import Iterable

from .exception import ProcessError
from .library.logger import log
from .sync import SyncExclude, SyncItem


class Scp:
    command: tuple[str, ...] = (
        "scp",
        "-r",  # recursive
        "-C",  # compression
        "-p",  # preserve modification times and modes
    )

    def __init__(self, hostname: str, local_base: str, remote_base: str, dry_run: bool = False) -> None:
        self.hostname = hostname
        self.local_base = local_base
        self.remote_base = remote_base
        self.dry_run = dry_run

    def _sync(self, src: str, dst: str, excludes: Iterable[str]) -> None:
        # TODO: scp has no native --exclude support.
        if excludes:
            log("Warning: SCP does not support excludes; exclusions will be ignored.")

        cmd = [
            *Scp.command,
            src,
            dst,
        ]

        result = subprocess.run(cmd)

        if result.returncode != 0:
            raise ProcessError("scp returned an error!", result.returncode)

    def _get_exclude_list(self, scp_items: Iterable[SyncItem]) -> list[str]:
        excludes: list[str] = []

        for scp_item in scp_items:
            if isinstance(scp_item, SyncExclude):
                excludes.append(scp_item.get_path())

        return excludes

    def _sync_multiple(
        self,
        scp_items: Iterable[SyncItem],
        src_hostname: str = "",
        src_path: str = "",
        dst_hostname: str = "",
        dst_path: str = "",
    ) -> None:
        excludes = self._get_exclude_list(scp_items)

        if excludes:
            log("Warning: SCP does not support excludes:")
            for exclude in excludes:
                log(f"  {exclude}")

        for scp_item in scp_items:
            if isinstance(scp_item, SyncExclude):
                continue

            src, dst = scp_item.parse(
                src_hostname=src_hostname,
                src_path=src_path,
                dst_hostname=dst_hostname,
                dst_path=dst_path,
            )

            log(f"Transferring: {src} to {dst}")

            if self.dry_run:
                continue

            self._sync(src, dst, excludes)

    def send(self, scp_items: Iterable[SyncItem]) -> None:
        self._sync_multiple(
            scp_items,
            src_path=self.local_base,
            dst_hostname=self.hostname,
            dst_path=self.remote_base,
        )

    def receive(self, scp_items: Iterable[SyncItem]) -> None:
        self._sync_multiple(
            scp_items,
            src_hostname=self.hostname,
            src_path=self.remote_base,
            dst_path=self.local_base,
        )
