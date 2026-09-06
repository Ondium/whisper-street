"""In-memory bookkeeping for asynchronous jobs.

TODO(worker): this store never moves a job past QUEUED. There is no worker
yet to run the pipeline and drive real transitions
(queued -> running -> succeeded/partial/failed, per
docs/api/README.md#job-lifecycle). When the Phase-1 engine lands, a worker
will import whisper_street.core.pipeline.default_pipeline() (or a
per-deployment Pipeline), run it against queued jobs, and call `put()` with
the updated JobStatus as it progresses. Until then, this class only ever
does the bookkeeping a caller can observe synchronously: create, look up,
and cancel.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import replace
from datetime import datetime, timezone

from whisper_street.core.types import JobState, JobStatus, PipelineConfig


def _now() -> str:
    """The current time as an ISO 8601 timestamp, UTC."""

    return datetime.now(timezone.utc).isoformat()


class InMemoryJobStore:
    """Thread-safe, process-local job bookkeeping.

    Not persistent: all jobs are lost on process restart. That's acceptable
    for a stub scaffold — there is no worker whose progress would need to
    survive a restart yet.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, JobStatus] = {}

    def create(self, config: PipelineConfig) -> JobStatus:
        """Create a new job in the QUEUED state.

        Args:
            config: The pipeline configuration the job was submitted with.
                Echoed back on every subsequent read of this job.

        Returns:
            The newly created JobStatus.
        """

        job_id = f"job_{uuid.uuid4().hex}"
        now = _now()
        status = JobStatus(
            job_id=job_id,
            state=JobState.QUEUED,
            created_at=now,
            updated_at=now,
            config=config,
        )
        with self._lock:
            self._jobs[job_id] = status
        return status

    def get(self, job_id: str) -> JobStatus | None:
        """Look up a job by id.

        Args:
            job_id: The job identifier returned by `create`.

        Returns:
            The current JobStatus, or None if no job has that id.
        """

        with self._lock:
            return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> JobStatus | None:
        """Move a job to the CANCELLED state.

        Args:
            job_id: The job identifier to cancel.

        Returns:
            The updated JobStatus, or None if no job has that id.
        """

        with self._lock:
            existing = self._jobs.get(job_id)
            if existing is None:
                return None
            updated = replace(existing, state=JobState.CANCELLED, updated_at=_now())
            self._jobs[job_id] = updated
            return updated

    def put(self, status: JobStatus) -> None:
        """Insert or replace a job wholesale, keyed by `status.job_id`.

        This is a test-only escape hatch: it lets tests inject a JobStatus
        in a state (e.g. SUCCEEDED with a Transcript) that no production
        code path produces yet, since no worker exists to produce one.

        Args:
            status: The JobStatus to store.
        """

        with self._lock:
            self._jobs[status.job_id] = status
