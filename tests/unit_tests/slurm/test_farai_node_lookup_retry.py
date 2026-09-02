"""The post-allocation node lookup retries transient empty results and nothing else."""
from typing import List, Tuple

import pytest

from sky.provision.slurm import instance


class _Client:

    def __init__(self, failures: int, error: str = 'No nodes found for job {job_id}.'):
        self.failures = failures
        self.error = error
        self.calls = 0

    def get_job_nodes(self, job_id: str) -> Tuple[List[str], List[str]]:
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError(self.error.format(job_id=job_id))
        return ['gb215'], ['10.0.0.1']


@pytest.fixture
def clock(monkeypatch):
    sleeps: List[float] = []
    monkeypatch.setattr(instance.time, 'sleep', sleeps.append)
    warnings: List[str] = []
    monkeypatch.setattr(instance.logger, 'warning', warnings.append)
    return sleeps, warnings


def test_empty_results_are_retried_until_nodes_appear(clock):
    sleeps, warnings = clock
    client = _Client(failures=2)

    assert instance._get_job_nodes_with_retry(client, '102017') == (['gb215'],
                                                                    ['10.0.0.1'])
    assert client.calls == 3
    assert sleeps == [instance.POLL_INTERVAL_SECONDS] * 2
    assert len(warnings) == 2


def test_a_persistent_failure_propagates_after_bounded_attempts(clock):
    sleeps, warnings = clock
    client = _Client(failures=6)

    with pytest.raises(RuntimeError, match='No nodes found for job 102017'):
        instance._get_job_nodes_with_retry(client, '102017')

    assert client.calls == 6
    assert sleeps == [instance.POLL_INTERVAL_SECONDS] * 5
    assert len(warnings) == 5


def test_other_runtime_errors_are_not_retried(clock):
    sleeps, warnings = clock
    client = _Client(failures=1, error='Failed to resolve hostname')

    with pytest.raises(RuntimeError, match='Failed to resolve hostname'):
        instance._get_job_nodes_with_retry(client, '102017')

    assert client.calls == 1
    assert sleeps == []
    assert warnings == []
