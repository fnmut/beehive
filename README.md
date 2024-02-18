A very simple example project demonstrating usage of OpenTelemetry spans, manual creation of OpenTelemetry exporters, and the Jaeger frontend for inspecting spans locally.

## Goals:

* Learning by doing - Understanding how to use OpenTelemetry tracing
* Demonstrate how to re-use parent spans to open new child spans
* Demonstrate local tooling helpful for viewing spans

## Setup

Create an .env file from the committed example. Fill it out.

```
cp .env.example .env
```

Also do `poetry install` and make sure your docker daemon is running.

## Run the project

### Optional: startup Jaeger
If you will be exporting to the local Jaeger container, run

```
./jaeger.sh
```

This runs in the foreground right now, and can be shutoff by sending `^C`

### Run the script

Use the python in the local .venv to run the project:

```
.venv/bin/python src/__init__.py
```

## View Traces

Depending on your configuration, this will send to Grafana Cloud or the local Jaeger container.
If you chose Jaeger, you will see the results in the UI at http://localhost:16686
If you chose Grafana cloud, you can find them in the "Explore" tab using the "Tempo" datasource.
