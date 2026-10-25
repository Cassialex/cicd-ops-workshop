# Exercise 1: CI/CD, reading and changing a pipeline

CI/CD stands for Continuous Integration and Continuous Deployment.
Here, we will look at a small CI/CD pipeline that runs checks when code gets pushed, and which allows you to manually launch a model training job.

## Goals

- Become familiar with CI/CD pipelines.
- Know where to look when something fails.
- Understand in which order jobs run.

## Getting started

You need [Git](https://git-scm.com/), [uv](https://docs.astral.sh/uv/getting-started/installation/), and an account on GitHub or GitLab.

1. Fork or upload this repository and clone it locally:
   - **GitHub**: 
   - **GitLab**: 
2. Open a terminal in the cloned local repository.
3. Install the dependencies:

   ```sh
   uv sync
   ```

4. Run the three checks on your machine. They should all pass.

   ```sh
   uv run ruff format --check .
   uv run ruff check .
   uv run pytest tests/ -v
   ```

5. Open your pipelines page. The first pipeline should be green.

Each task asks you to change some code, then push it:

```sh
git add .
git commit -m "Describe your change"
git push
```

> **Before you start**
>
> - Do not run `pre-commit install` yet. It would fix the code style for you on every commit, and Task 1 would not fail.
> - Turn off "format on save" in your editor, for the same reason.

## Tasks

Short tasks to help build intuition.

### Task 1: Bad formatting & Code Incongruence

1. In `src/ci_cd/train.py`, add `import os`
2. Commit and push.
3. Open the new pipeline.

**Questions**

- Which job failed?
- What does its log say?
- How do you fix it?

<details>
<summary>Hint</summary>

Click on the job with the red cross.
The log is long: scroll to the end first.
Look for the command that failed, and the lines just below it.

</details>

<details>
<summary>Answer</summary>

The `lint` job failed.
Its second command, `uv run ruff check .`, printed this:

```text
F401 [*] `os` imported but unused
 --> src/ci_cd/train.py:2:8
  |
1 | import json
2 | import os
  |        ^^
3 | import pathlib
  |
help: Remove unused import: `os`
  |
1 | import json
  - import os
2 | import pathlib
  |

Found 1 error.
[*] 1 fixable with `--fix`.
```

The lines with `-` show your code, and the lines with `+` show what ruff expects.
To fix it, let ruff format the code on your machine, then commit and push again:

```sh
uv run ruff check --fix .
```

> **On GitHub** - Undo your last edit and commit again.

The `lint` job runs two tools:

- `ruff format` only changes the layout: spaces, quotes, line breaks. It never changes what the code does.
- `ruff check` reads the code without running it, and flags likely bugs, such as an unused import or a misspelled variable name.

Installing the pre-commit, or configuring your IDE to format on save, will ensure that the lint job always passes.

</details>

### Task 2: Do the other jobs still run?

Look again at the failed pipeline from Task 1.

**Questions**

- Did the `test` job run?
- Why, or why not?
- How could you change this?

<details>
<summary>Hint</summary>

Compare the pipeline graph with the pipeline file of your platform.
Look up the `needs` keyword in its documentation:
[GitLab](https://docs.gitlab.com/ci/yaml/#needs) or
[GitHub](https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow#defining-prerequisite-jobs).

</details>

<details>
<summary>Answer</summary>

The answer depends on the platform.

**GitLab**: no, `test` was skipped.
Stages run one after the other, and a failed stage stops the stages after it.
`lint` is in stage `lint`, so `test` never started.
You can change this in two ways:

- Add `needs: []` to the `test` job. The job then no longer waits for the earlier stages.
- Add `allow_failure: true` to the `lint` job. The pipeline then continues after it fails, and shows a warning instead.

**GitHub**: yes, `test` ran.
Jobs run in parallel unless a job lists another job under `needs`.
To make `test` wait for `lint`, add this to the `test` job:

```yaml
    needs: lint
```

Neither choice is wrong per se.
Stopping early saves time and compute.
Running everything shows you all the problems at once.
Which one you should choose depends on whether it makes sense to run other jobs when one fails.

Generally the standard in teams becomes "all checks must pass". So if the linter (which is usually much faster than the tests) fails, it's already a sign that whoever made the change should fix it locally before pushing again.

</details>

### Task 3: A weaker model

1. In `src/ci_cd/train.py`, set `N_ESTIMATORS = 1` and `MAX_DEPTH = 1`.
   The model is now a single tree that can make only one split.
2. Commit and push.

**Questions**

- Which jobs pass?
- What is the new accuracy of the model? Where did you find it?
- Does it pass all the tests?
- Run the training on your machine with `uv run python -m ci_cd.train`. Does the training itself complete?

When you are done, set both values back to what they were: `N_ESTIMATORS = 10` and `MAX_DEPTH = None` and push.

<details>
<summary>Hint</summary>

The accuracy is checked in `tests/test_model.py`.
Read the failed job's log from the bottom up.

</details>

<details>
<summary>Answer</summary>

`lint` passes: the code is still valid and well formatted.
`test` fails:

```text
FAILED tests/test_model.py::test_model_accuracy - AssertionError: Accuracy 0.70 is below threshold 0.80
```

The new accuracy is 0.70.
The test sets the threshold with `MIN_ACCURACY = 0.8`.
`test_version.py` still passes.

The training on your machine completes without errors, and prints `Accuracy: 0.7000`.
The training does not check quality.
The CI only stops a bad model because a test checks for it.
A pipeline protects you from the problems you write checks for, and from no others.

</details>

### Task 4: An empty test set

1. In `src/ci_cd/train.py`, set `TEST_SIZE = 0`.
   This keeps no data back to evaluate the model.
2. Commit and push.

**Questions**

- Which job fails first?
- What does the error say? Which line of our own code triggered it?
- How could we have avoided pushing broken code in the first place?

When you are done, set the value back to `TEST_SIZE = 0.2`.

<details>
<summary>Hint</summary>

This log is longer, because the error comes from inside scikit-learn.
Start at the bottom, at the `short test summary info`.
Then look for the lines that start with `E`.
Then scroll up to the part of the traceback that points to a file in `src/ci_cd/`.

</details>

<details>
<summary>Answer</summary>

`lint` passes and `test` fails.
On GitLab, `test` is the first stage that fails.
On GitHub, both jobs run at the same time, and only `test` fails.

The error says:

```text
InvalidParameterError: The 'test_size' parameter of train_test_split must be a float in the range (0.0, 1.0), an int in the range [1, inf) or None. Got 0 instead.
```

Two tests stop with this error: `test_model_accuracy` fails, and `test_predict` errors in its `client` fixture, because both call `train()`.
The traceback points to the `train_test_split` call in `load_data()`, in `src/ci_cd/train.py`.
The code fails at the split, before the training even starts, because scikit-learn checks its inputs.

To avoid pushing broken code:

- Run the same commands on your machine before you push: `uv run pytest tests/ -v`.
- Let your computer do that for you, with a Git hook. See the extension "Run the tests before you push".
- Work on a branch, and protect the `main` branch so a change can only be merged once its pipeline passes.
  Broken code can then still reach a branch, but never `main`.

</details>

## Extensions

The extensions are optional.
They are more involved and more open-ended than the tasks.
Only start one once you're happy with the tasks.

Read through all the extensions first.
Pick the one you find most interesting, and that you think you can do in the time left.
If anything is unclear, ask an instructor.

### Run the tests before you push

**Goal**: `git push` refuses to push when a test fails, before anything reaches the CI.

**Why**: the fastest feedback comes from your own machine.

**Done when**: you push a commit with `TEST_SIZE = 0`, and the push stops on your machine with the test error.

**Pointers**

- [pre-commit](https://pre-commit.com/) runs hooks at different Git steps. `.pre-commit-config.yaml` already has some.
- Add a hook with `repo: local` that runs `uv run pytest`, with `stages: [pre-push]`.
- Install it with `uv run pre-commit install --hook-type pre-push`.

### Choose the training settings when you start the pipeline

**Goal**: start the `train` job with your own values for `N_ESTIMATORS` and `MAX_DEPTH`, without changing the code.

**Why**: you can try out settings without a new commit for each one.

**Done when**: you start the job with other values, and its log shows another accuracy.

**Pointers**

- In `train.py`, read the values from environment variables, for example `int(os.getenv("N_ESTIMATORS", "10"))`.
- **GitLab**: you can set variables when you [run a pipeline manually](https://docs.gitlab.com/ci/pipelines/#run-a-pipeline-manually), or when you start a manual job.
- **GitHub**: add [`inputs` to `workflow_dispatch`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch), and pass them to the job as `env`.

### A smarter quality gate

**Goal**: a test that fails unless the model beats a simple baseline.

**Why**: a fixed threshold such as 0.8 is arbitrary. "Better than guessing" is easier to argue for.

**Done when**: a new test compares the model with a baseline. It passes for the real model, and fails when you swap the model for the baseline itself.

**Pointers**

- scikit-learn's [`DummyClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) always predicts the most frequent class.
- Decide by how much the model must beat it.

### Test on several Python versions

**Goal**: the `test` job runs once for each of Python 3.12, 3.13 and 3.14.

**Why**: your users don't all have the same Python version as you.

**Done when**: your pipeline shows one `test` job per Python version.

**Pointers**

- **GitLab**: [`parallel:matrix`](https://docs.gitlab.com/ci/yaml/#parallelmatrix), with the version in the image name, for example `python:$PYTHON_VERSION`.
- **GitHub**: [a matrix strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs), and `uv sync --python ${{ matrix.python-version }}`.

### Speed up the pipeline with a cache

**Goal**: the jobs reuse the downloaded packages from earlier runs.

**Why**: without a cache, every job downloads all dependencies again. That is most of its run time.

**Done when**: you can compare the duration of a job with and without the cache.

**Pointers**

- **GitLab**: there is no cache yet. See [caching in GitLab CI/CD](https://docs.gitlab.com/ci/caching/), and uv's [GitLab guide](https://docs.astral.sh/uv/guides/integration/gitlab/).
- **GitHub**: `setup-uv` already caches by default. Turn it off with `enable-cache: false`, compare the durations, and find the lines in the log where the cache is restored. See [caching in `setup-uv`](https://github.com/astral-sh/setup-uv/blob/main/docs/caching.md).

### Train only when it matters

**Goal**: `train` runs on its own, but only on the `main` branch, and only when a file in `src/` changed.

**Why**: training is often the slowest and most expensive job.

**Done when**: a push to `main` that changes `train.py` trains the model, and a push that only changes this README does not.

**Pointers**

- **GitLab**: [`rules`](https://docs.gitlab.com/ci/yaml/#rules), with `if` and `changes`.
- **GitHub**: [`paths`](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) on the `push` trigger, and `if` on the job.
  A separate workflow file for `train` may be simpler.
