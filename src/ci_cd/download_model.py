import io
import os
import zipfile

import requests

from ci_cd.inference import MODEL_PATH

API_URL = "https://api.github.com"
ARTIFACT_NAME = "model"


def main() -> None:
    """Download the model from the artifacts of a training run into `model/`."""
    repository = os.environ["GITHUB_REPOSITORY"]  # e.g. `<you>/<repository>`
    run_id = os.getenv("MODEL_RUN_ID", "latest")  # `latest`, or the ID of a run
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    }

    artifact = find_artifact(
        repository=repository,
        run_id=run_id,
        headers=headers,
    )
    print(
        f"Downloading the model of run {artifact['workflow_run']['id']}, "
        f"created at {artifact['created_at']}"
    )
    download(
        url=artifact["archive_download_url"],
        headers=headers,
    )
    print(f"Model saved to {MODEL_PATH.parent}/")


def find_artifact(repository: str, run_id: str, headers: dict) -> dict:
    """Return the newest model artifact of one run, or of the whole repository."""
    if run_id == "latest":
        url = f"{API_URL}/repos/{repository}/actions/artifacts"
    else:
        url = f"{API_URL}/repos/{repository}/actions/runs/{run_id}/artifacts"
    response = requests.get(
        url,
        headers=headers,
        params={"name": ARTIFACT_NAME},
        timeout=30,
    )
    response.raise_for_status()

    artifacts = [a for a in response.json()["artifacts"] if not a["expired"]]
    if not artifacts:
        raise SystemExit(f"No `{ARTIFACT_NAME}` artifact found for run `{run_id}`")
    return max(artifacts, key=lambda a: a["created_at"])


def download(url: str, headers: dict) -> None:
    # GitHub redirects to a storage server, and `requests` does not send it the token.
    response = requests.get(
        url,
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(MODEL_PATH.parent)


if __name__ == "__main__":
    main()
