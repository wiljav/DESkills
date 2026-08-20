# Troubleshooting Setup

Common failures when bootstrapping the DE toolchain, with the fix that
resolves each.

## Docker daemon not running

Symptom: `docker info` errors with "Cannot connect to the Docker daemon".

Fix: start Docker Desktop (macOS/Windows) or `systemctl start docker`
(Linux), wait for the engine, and re-run `docker info`. The Airflow section of
the stack setup skill cannot proceed until this passes.

## Port 8080 already in use

Symptom: `airflow standalone` fails to bind or the UI is served by another app.

Fix: either stop the conflicting process or change the webserver port in
`airflow.cfg` (`web_server_port`). Document the chosen port in the project
README so agents do not fight over it.

## uv not found after install

Symptom: installer succeeded but `uv` is not on PATH.

Fix: the installer targets `~/.local/bin`. Add the directory to your shell
profile, or run `export PATH="$HOME/.local/bin:$PATH"` for the session.

## Python version mismatch in Airflow

Symptom: `airflow standalone` crashes with `ModuleNotFoundError` or version
errors after a Python upgrade.

Fix: Airflow environments must be recreated after a Python upgrade. Delete the
old virtual environment, recreate it with the current Python, and reinstall
the pinned requirements. Never run Airflow from a system-wide Python.

## PySpark crashes on Apple Silicon

Symptom: `pyspark` raises errors about missing native libraries or
`libjvm.dylib`.

Fix: install a JDK 17+ (e.g. `brew install openjdk@17`) and ensure
`JAVA_HOME` is exported before launching Spark. The `spark-basics` skill
documents the exact environment variables.
