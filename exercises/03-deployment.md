# Exercise 3: Deployment, serve the model in a container

The training gives us a model in the `model` artifact of a workflow run.
Now we want to serve it: a small web API that answers with the class of a flower, running in a container.

You only change `src/ci_cd/api.py`, `tests/test_api.py` and `.github/workflows/deploy.yml`.

## Goals

- Run a model behind an API, in a container.
- Know which model version is deployed, and choose it on purpose.
- Give the platform that runs the container a way to check that it is alive.

## The files

- `src/ci_cd/api.py` is a [FastAPI](https://fastapi.tiangolo.com/) application.
  It loads `model/model.pkl` when it starts, and answers on `POST /predict`.
- `src/ci_cd/download_model.py` downloads the `model` artifact of a training run into `model/`.
  It reads three environment variables:
  - `GITHUB_REPOSITORY`: the repository to take the model from, e.g. `<you>/<repository>`.
  - `GITHUB_TOKEN`: a token that can read the repository's workflow runs.
  - `MODEL_RUN_ID`: the training run to take the model from, or `latest` for the newest one.
- `deployment.Dockerfile` builds the image that serves the model.
  When a container starts, it first downloads the model, then starts the server.
- `.github/workflows/deploy.yml` builds that image, starts a container, and sends it two flowers to classify.
  It only runs when you press **Run workflow**.

## Tasks

### Task 1: Deploy a model

The **Deploy** workflow needs at least one `model` artifact in your fork.
Artifacts are not copied when you fork a repository.

1. If you haven't trained a model in your fork yet, open the **Actions** tab, select **CI** on the left, and click **Run workflow**.
   If you did Exercise 2, every push already trains a model.
2. Select **Deploy** on the left, and click **Run workflow**.
3. Open the run, and the `deploy` job.

**Questions**

- Which training run did the model come from? Where do you find it in the log?
- When is the model downloaded: when the image is built, or when the container starts?
- Why does the step **Wait for the API** retry, instead of sending one request?
- The image is built with `-f deployment.Dockerfile`. Why not use the `Dockerfile` from Exercise 2?

<details>
<summary>Hint</summary>

- The model's run is printed by `download_model.py`. Its output is in the step **Show the container logs**.
- Look at the `CMD` in `deployment.Dockerfile`, and at the comment above it.
- `-f` selects which file `docker build` reads. Without it, `docker build` reads `Dockerfile`.

</details>

<details>
<summary>Answer</summary>

The step **Show the container logs** starts with:

```text
Downloading the model of run <run ID>, created at <date>
Model saved to model/
```

followed by the logs of the server and of the two requests.
The run ID is the number in the address of the training run's page: `https://github.com/<you>/<repository>/actions/runs/<run ID>`.

The model is downloaded when the container starts.
That way the image holds no token and no model, and the same image can serve any model: you choose it with `-e MODEL_RUN_ID=...` when you start the container.
The cost is a slower start, and a container that fails to start when GitHub can't be reached.

The container needs a few seconds to download the model and start the server.
Until then, the requests fail, e.g. with `Connection reset by peer`.
`--retry` sends the request again until the server answers, or until it gives up.

The two images do different jobs: one trains, the other serves.
They share the same `requirements.txt`, so the server has the same version of scikit-learn as the training.
A model saved with one version of scikit-learn may not load with another one.

</details>

### Task 2: Pin the model version

`MODEL_RUN_ID: latest` deploys whichever model was trained last.
Any new training run changes what the next deployment serves, without a change to `deploy.yml`.

1. Train a second model: run **CI** again, or push a change if you did Exercise 2.
2. Pick the training run whose model you want to serve, and copy its run ID.
3. In `.github/workflows/deploy.yml`, set `MODEL_RUN_ID` to that run ID. Push.
4. Run **Deploy** again.

**Questions**

- Which run did the model come from this time?
- Train another model, and run **Deploy** again. Which model does it serve now? And with `latest`?
- Artifacts are kept for 30 days. What happens to your deployment after that?

**Done when**: the log of **Deploy** shows the run ID you chose, after a newer model was trained.

<details>
<summary>Hint</summary>

- The run ID is the number at the end of the address of the run's page.
- Pick a run that has a `model` artifact, at the bottom of the run's page.
- Write the ID in quotes, e.g. `MODEL_RUN_ID: "1234567890"`.

</details>

<details>
<summary>Answer</summary>

```yaml
    env:
      # The training run whose `model` artifact to serve. `latest` takes the newest one.
      MODEL_RUN_ID: "1234567890"
```

The pinned deployment serves the model of that run, however many models are trained after it.
With `latest`, it serves the newest one, whether or not you checked it.

The deployed version is now written in Git: you can see which model is in production, review a change of version like any change of code, and go back to the previous version with `git revert`.

After 30 days, the artifact expires, and `download_model.py` stops with ``No `model` artifact found for run ...``.
Run artifacts are a stand-in for a model registry, e.g. [MLflow](https://mlflow.org/docs/latest/ml/model-registry/), which keeps every version until you delete it.

</details>

### Task 3: A health check

A platform that runs containers, e.g. Kubernetes or a cloud service, regularly checks that each container is still alive.
It sends a request to an endpoint such as `/health`, and restarts the container when the answer is not `200 OK`.

1. In `src/ci_cd/api.py`, add a `GET /health` endpoint that answers `{"status": "ok"}`.
2. In `tests/test_api.py`, add a test for it.
3. In `.github/workflows/deploy.yml`, complete the `TODO (Task 3)`: wait for `/health` instead of `/docs`.
4. Push, and run **Deploy**.

**Questions**

- Which jobs check your new endpoint?
- `/docs` also answered once the server was up. Why is `/health` a better choice?

**Done when**: the `test` job runs your new test, and the step **Wait for the API** of **Deploy** waits for `/health`.

<details>
<summary>Hint</summary>

- Look at how `/predict` is defined in `api.py`. A `GET` endpoint is defined with `@app.get(...)`.
- A function can return a `dict`: FastAPI turns it into JSON.
- In `tests/test_api.py`, the `client` fixture starts the API. Write a `test_health(client)` function like `test_predict`, that sends a request with `client.get("/health")`, and checks the status code and the JSON of the response.
- Run the tests on your machine with `uv run pytest tests/ -v`, if you have it set up.

</details>

<details>
<summary>Answer</summary>

In `src/ci_cd/api.py`:

```python
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

In `tests/test_api.py`:

```python
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

In `.github/workflows/deploy.yml`:

```yaml
      - name: Wait for the API
        run: curl --fail --silent --show-error --retry 30 --retry-all-errors --retry-delay 2 http://localhost:8000/health
```

The `test` job of **CI** runs `test_health` on every push, without a container.
The **Deploy** workflow checks the endpoint in the container that was just built.

`/docs` is a page for people, made by FastAPI, and it may be turned off in production.
`/health` is a contract with the platform: it always exists, is cheap to answer, and can be extended to check more, e.g. that the model is loaded.

</details>

## Extensions

The extensions are optional.
Only start one once you're happy with the tasks.

### Let Docker check the health

**Goal**: the image itself says how to check that a container is healthy.

**Done when**: `docker ps` shows the container as `(healthy)`, e.g. in a step of **Deploy** after **Wait for the API**.

**Pointers**

- The [`HEALTHCHECK`](https://docs.docker.com/reference/dockerfile/#healthcheck) instruction in `deployment.Dockerfile`.
- The `slim` image has no `curl`. Use Python instead: `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"`.
- Give the container time to download the model before the first check, with `--start-period`.

### Deploy the model you just trained

**Goal**: every push trains a model, then deploys exactly that model.

**Done when**: a push runs `build`, then `train`, then `deploy`, and the log of `deploy` shows the run ID of the same run.

**Pointers**

- Do Exercise 2 first: `docker.yml` calls `train-docker.yml` after the build.
- Add `workflow_call` to `deploy.yml`, with an input for the run ID, like `train-docker.yml` has for the image tag.
- A job that calls another workflow runs in the same run: its ID is `${{ github.run_id }}`.
- The called workflow can only have the permissions of the caller: `docker.yml` needs `actions: read`.

### Run the server on your machine

**Goal**: send your own requests to the API, from your machine.

**Done when**: `http://localhost:8000/docs` opens in your browser, and you classify a flower from there.

**Pointers**

- You need Docker, and a [fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with read access to **Actions** on your fork.
- Build the image with `docker build -f deployment.Dockerfile -t iris-api .`.
- Pass the variables with `-e`, e.g. `-e GITHUB_REPOSITORY=<you>/<repository>`, and the port with `-p 8000:8000`.
- Never commit the token. If you write it in a file, e.g. `.env` for `docker run --env-file .env`, add the file to `.gitignore`.
