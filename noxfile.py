import nox


@nox.session(
    python=["3.8", "3.9", "3.10"], venv_backend="conda", reuse_venv=True
)
def backend_tests(session: nox.Session) -> None:
    session.install("pytest-cov", "fastapi", "uvicorn", "httpx")
    session.run(
        "pytest",
        "--cov",
        "--cov-report",
        "term",
        "--cov-report",
        f"xml:coverage.{session.python}.xml",
        env={"COVERAGE_FILE": f".coverage.{session.python}"},
    )
    session.notify("cover")


@nox.session
def cover(session: nox.Session) -> None:
    """Coverage analysis."""
    session.install("coverage[toml]")
    session.run("coverage", "combine")
    session.run("coverage", "xml")
