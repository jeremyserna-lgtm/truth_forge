"""ClusterExecutionTool - native execution over SSH (docker-free).

This implementation runs locally when node == "local"/"king"/"localhost".
SSH support is scaffolded for future cluster use (no Docker fallback).
"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from truth_forge.governance import assert_not_armed


if TYPE_CHECKING:
    from truth_forge.services.cluster_state import ClusterStateMonitor


DEFAULT_DENY = [
    "rm -rf /",
    "mkfs",
    "dd if=/dev/zero",
    ":(){ :|:& };:",  # fork bomb
    "shutdown",
    "reboot",
]


def _contains_denied(command: str, denylist: Iterable[str]) -> str | None:
    lowered = command.lower()
    for pattern in denylist:
        if pattern.lower() in lowered:
            return pattern
    return None


def _wrap_with_limits(
    command: list[str], cpu_quota: int | None, mem_limit_mb: int | None
) -> list[str]:
    """Prefix command with POSIX resource limits when provided."""
    if not cpu_quota and not mem_limit_mb:
        return command

    limit_parts = []
    if cpu_quota:
        limit_parts.append(f"ulimit -t {cpu_quota}")
    if mem_limit_mb:
        # set virtual memory limit (KB)
        kb = mem_limit_mb * 1024
        limit_parts.append(f"ulimit -v {kb}")

    limits = " && ".join(limit_parts)
    return ["bash", "-lc", f"{limits} && exec {' '.join(command)}"]


@dataclass
class ExecutionResult:
    node: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    workdir: str


@dataclass
class ClusterExecutionTool:
    """Execute code on Genesis cluster nodes via SSH (or locally for now)."""

    ssh_user: str = "genesis"
    ssh_key: Path = field(default_factory=lambda: Path("~/.ssh/id_king").expanduser())
    ssh_port: int = 22
    denylist: list[str] = field(default_factory=lambda: list(DEFAULT_DENY))
    timeout: int = 300
    cpu_quota: int | None = None  # seconds
    mem_limit_mb: int | None = None
    preferred_nodes: list[str] = field(default_factory=lambda: ["king"])
    cluster_state: ClusterStateMonitor | None = None

    def __post_init__(self) -> None:
        if self.cluster_state is None:
            try:
                from truth_forge.services.cluster_state import ClusterStateMonitor

                self.cluster_state = ClusterStateMonitor(nodes=self.preferred_nodes)
            except Exception:
                self.cluster_state = None

    def execute(
        self,
        command: str,
        node: str = "local",
        language: str = "bash",
        workdir: Path | None = None,
        env: dict[str, str] | None = None,
        dry_run: bool = False,
        stream: bool = False,
    ) -> ExecutionResult:
        """Execute a command on the specified node (local only in this impl)."""
        assert_not_armed()

        denied = _contains_denied(command, self.denylist)
        if denied:
            raise PermissionError(f"Command blocked by denylist pattern: {denied}")

        if language not in {"bash", "python"}:
            raise ValueError("language must be 'bash' or 'python'")

        workdir = workdir or Path(tempfile.mkdtemp(prefix="genesis_exec_"))

        if node == "any":
            node = self._pick_node()

        if dry_run:
            return ExecutionResult(
                node=node,
                command=command,
                exit_code=0,
                stdout=f"[DRY_RUN] {command}",
                stderr="",
                duration_ms=0.0,
                workdir=str(workdir),
            )

        if node == "any":
            node = self._pick_node()

        start = time.time()
        try:
            if node in {"local", "king", "localhost"}:
                return self._execute_local(command, language, workdir, node, start, env, stream)
            return self._execute_ssh(command, language, workdir, node, start, env, stream)
        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start) * 1000
            return ExecutionResult(
                node=node,
                command=command,
                exit_code=124,
                stdout=e.stdout or "",
                stderr=f"Timeout after {self.timeout}s",
                duration_ms=duration_ms,
                workdir=str(workdir),
            )

    def _execute_local(
        self,
        command: str,
        language: str,
        workdir: Path,
        node: str,
        start: float,
        env: dict[str, str] | None,
        stream: bool,
    ) -> ExecutionResult:
        base_cmd = ["python3", "-c", command] if language == "python" else ["bash", "-lc", command]

        cmd = _wrap_with_limits(base_cmd, self.cpu_quota, self.mem_limit_mb)

        if stream:
            proc = subprocess.Popen(
                cmd,
                cwd=str(workdir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, **(env or {})},
                start_new_session=True,
            )
            stdout_chunks = []
            stderr_chunks = []
            start_time = time.time()
            try:
                while proc.poll() is None:
                    if proc.stdout:
                        line = proc.stdout.readline()
                        if line:
                            stdout_chunks.append(line)
                    if proc.stderr:
                        line = proc.stderr.readline()
                        if line:
                            stderr_chunks.append(line)
                    if time.time() - start > self.timeout:
                        proc.kill()
                        raise subprocess.TimeoutExpired(cmd, self.timeout)
                # drain remaining
                if proc.stdout:
                    stdout_chunks.extend(proc.stdout.readlines())
                if proc.stderr:
                    stderr_chunks.extend(proc.stderr.readlines())
            finally:
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                node=node,
                command=command,
                exit_code=proc.returncode or 0,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
                duration_ms=duration_ms,
                workdir=str(workdir),
            )

        proc = subprocess.run(
            cmd,
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env={**os.environ, **(env or {})},
        )
        duration_ms = (time.time() - start) * 1000
        return ExecutionResult(
            node=node,
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_ms=duration_ms,
            workdir=str(workdir),
        )

    def _execute_ssh(
        self,
        command: str,
        language: str,
        workdir: Path,
        node: str,
        start: float,
        env: dict[str, str] | None,
        stream: bool,
    ) -> ExecutionResult:
        # Remote temp dir per run
        remote_tmp = f"/tmp/genesis_exec_{int(start)}"
        exports = ""
        if env:
            exports = " ".join([f"{k}={shlex.quote(v)}" for k, v in env.items()])
        limits = []
        if self.cpu_quota:
            limits.append(f"ulimit -t {self.cpu_quota}")
        if self.mem_limit_mb:
            kb = self.mem_limit_mb * 1024
            limits.append(f"ulimit -v {kb}")
        limits_cmd = " && ".join(limits)

        wrapper = f"mkdir -p {remote_tmp} && cd {remote_tmp} && "
        if limits_cmd:
            wrapper += f"{limits_cmd} && "
        if exports:
            wrapper += f"export {exports} && "
        if language == "python":
            wrapper += f"python3 -c {shlex.quote(command)}"
        else:
            wrapper += f"bash -lc {shlex.quote(command)}"

        ssh_cmd = [
            "ssh",
            "-i",
            str(self.ssh_key),
            "-p",
            str(self.ssh_port),
            f"{self.ssh_user}@{node}",
            wrapper,
        ]

        if stream:
            proc = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout_chunks: list[str] = []
            stderr_chunks: list[str] = []
            start_time = time.time()
            try:
                while proc.poll() is None:
                    if proc.stdout:
                        line = proc.stdout.readline()
                        if line:
                            stdout_chunks.append(line)
                    if proc.stderr:
                        line = proc.stderr.readline()
                        if line:
                            stderr_chunks.append(line)
                    if time.time() - start > self.timeout:
                        proc.kill()
                        raise subprocess.TimeoutExpired(ssh_cmd, self.timeout)
                if proc.stdout:
                    stdout_chunks.extend(proc.stdout.readlines())
                if proc.stderr:
                    stderr_chunks.extend(proc.stderr.readlines())
            finally:
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                node=node,
                command=command,
                exit_code=proc.returncode or 0,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
                duration_ms=duration_ms,
                workdir=str(workdir),
            )

        proc = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        duration_ms = (time.time() - start) * 1000
        return ExecutionResult(
            node=node,
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_ms=duration_ms,
            workdir=str(workdir),
        )

    def _pick_node(self) -> str:
        """Pick a node from preferred list; placeholder uses cluster_state if present."""
        if self.cluster_state:
            return self.cluster_state.pick_least_loaded()
        return self.preferred_nodes[0] if self.preferred_nodes else "local"

    # Placeholder for future distributed support
    def execute_distributed(self, commands: dict[str, str]) -> dict[str, ExecutionResult]:
        """Execute a mapping of node -> command (local only for now)."""
        results: dict[str, ExecutionResult] = {}
        for node, cmd in commands.items():
            results[node] = self.execute(cmd, node=node)
        return results
