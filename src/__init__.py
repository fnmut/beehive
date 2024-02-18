import base64
import os
import uuid
import random
from time import sleep
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGRPC,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from dotenv import load_dotenv

load_dotenv()

# Resource can be required for some backends, e.g. Jaeger
# If resource wouldn't be set - traces wouldn't appears in Jaeger
resource = Resource(attributes={"service.name": "taskmanager"})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)


def grafana_exporter():
    user = os.getenv("GRAFANA_USER")
    password = os.getenv("GRAFANA_API_KEY")
    endpoint = os.getenv("GRAFANA_ENDPOINT")
    # Configure the OTLP exporter with Basic Authentication
    creds = f"{user}:{password}"
    creds = creds.encode()
    return OTLPSpanExporter(
        endpoint=endpoint,
        headers={"Authorization": f"Basic {base64.b64encode(creds).decode()}"},
    )


def jaeger_exporter():
    endpoint = os.getenv("JAEGER_ENDPOINT")
    # Configure a local OLTP exporter
    return OTLPSpanExporterGRPC(
        insecure=True,
        endpoint=endpoint,
    )


def create_exporter():
    if os.getenv("USE_JAEGER_ENDPOINT") != "true":
        return grafana_exporter()
    else:
        return jaeger_exporter()


span_processor = BatchSpanProcessor(create_exporter())
trace.get_tracer_provider().add_span_processor(span_processor)


class Hive:
    datastore = {}

    def store_data(self, key, value):
        self.datastore[key] = value

    def retrieve_data(self, key):
        return self.datastore[key]

    def remove_data(self, key):
        del self.datastore[key]

    def select_random_key(self):
        # Select a random key from the datastore
        keys = list(self.datastore.keys())
        random.shuffle(keys)
        return keys[0]

    def num_records(self):
        return len(self.datastore)

    def pop_random_data(self):
        # Pop a random key from the datastore
        key = self.select_random_key()
        value = self.retrieve_data(key)
        self.remove_data(key)
        return (key, value)


def sleep_random(min: int, max: int):
    # Sleep for a random amount of seconds
    sleep(random.randint(min, max))


# initialize the Hive with some random data
hive = Hive()


def open_new_task():
    with tracer.start_as_current_span("task_open") as span:
        sleep_random(1, 2)
        id = uuid.uuid4()
        span.set_attribute("task_id", str(id))
        # span_context = span.get_span_context()
        hive.store_data(id, {"span": span, "status": "open"})
        print(f"Stored Task #{id}")


def close_out_task(id: uuid.UUID):
    task = hive.retrieve_data(id)
    with trace.use_span(task["span"]):
        with tracer.start_as_current_span("task_close") as span:
            sleep_random(1, 5)
            span.set_attribute("task_id", str(id))
            hive.remove_data(id)
            print(f"Closed Task #{id}")


if __name__ == "__main__":
    open_new_task()
    open_new_task()
    open_new_task()

    while hive.num_records() > 0:
        sleep_random(5, 10)
        key = hive.select_random_key()
        close_out_task(key)
