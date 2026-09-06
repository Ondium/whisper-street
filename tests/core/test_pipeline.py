import pytest

from whisper_street.core.pipeline import default_pipeline
from whisper_street.core.types import PipelineConfig


def test_default_pipeline_run_raises_on_ingest_stub() -> None:
    pipeline = default_pipeline()
    with pytest.raises(NotImplementedError, match="ingest"):
        pipeline.run("does-not-matter.wav", PipelineConfig())
