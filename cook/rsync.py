import shlex
import subprocess
from collections.abc import Iterable

from .exception import ProcessError
from .library.logger import log
from .sync import SyncExclude, SyncItem


class Rsync:
    command: tuple[str, ...] = (
        "rsync",
        "--compress",
        "--delete",
        "--links",
        "--recursive",
        "--mkpath",
        "--times",
        "--info=progress2",
    )
    exclude: str = "--exclude="

    # TODO: add rsync for local build
    def __init__(self, hostname: str, local_base: str, remote_base: str, dry_run: bool = False) -> None:
        self.hostname = hostname
        self.local_base = local_base
        self.remote_base = remote_base
        self.dry_run = dry_run

    def _sync(self, src: str, dst: str, exludes: Iterable[str]) -> None:
        cmd = list(Rsync.command)
        cmd.append(src)
        cmd.append(dst)
        cmd.extend([Rsync.exclude + e for e in exludes])

        result = subprocess.run(shlex.join(cmd), shell=True)
        if result.returncode != 0:
            raise ProcessError("rsync returned an error!", result.returncode)

    def _get_exclude_list(self, rsync_items: Iterable[SyncItem]) -> list[str]:
        excludes: list[str] = []
        for rsync_item in rsync_items:
            if isinstance(rsync_item, SyncExclude):
                excludes.append(rsync_item.get_path())
        return excludes

    def _sync_multiple(
        self, rsync_items: Iterable[SyncItem], src_hostname: str = "", src_path: str = "", dst_hostname: str = "", dst_path: str = ""
    ) -> None:
        excludes = self._get_exclude_list(rsync_items)

        if excludes:
            log("Excluding:")
            for exclude in excludes:
                log(f"  {exclude}")

        for rsync_item in rsync_items:
            if isinstance(rsync_item, SyncExclude):
                continue

            src, dst = rsync_item.parse(src_hostname=src_hostname, src_path=src_path, dst_hostname=dst_hostname, dst_path=dst_path)

            log(f"Transferring: {src} to {dst}")

            if self.dry_run:
                continue

            self._sync(src, dst, excludes)

    def send(self, rsync_items: Iterable[SyncItem]) -> None:
        self._sync_multiple(
            rsync_items,
            src_path=self.local_base,
            dst_hostname=self.hostname,
            dst_path=self.remote_base,
        )

    def receive(self, rsync_items: Iterable[SyncItem]) -> None:
        self._sync_multiple(
            rsync_items,
            src_hostname=self.hostname,
            src_path=self.remote_base,
            dst_path=self.local_base,
        )
