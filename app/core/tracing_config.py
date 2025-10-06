# app/core/tracing_config.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def configure_tracing(agent_host: str = "localhost", agent_port: int = 6831):
    trace.set_tracer_provider(TracerProvider())

    jaeger_exporter = JaegerExporter(
        agent_host_name=agent_host,
        agent_port=agent_port,
    )

    trace.get_tracer_provider().add_span_processor(          # type: ignore[attr-defined]
        BatchSpanProcessor(jaeger_exporter)
    )
