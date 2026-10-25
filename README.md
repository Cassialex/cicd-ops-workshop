# CI/CD and containers

> **MLOps & DevOps Workshop**

In this module, you change a small machine learning project and let the CI/CD pipeline check, build, train and deploy it for you.
You only need a browser and an account on GitHub.

## Exercises

1. [CI/CD: reading and changing a pipeline](exercises/01-cicd.md)
2. [Containers: build, push and train in an image](exercises/02-containers.md)
3. [Deployment: serve the model in a container](exercises/03-deployment.md)

Container demo located in the `docker_demo` directory in case you are curious.

## Setup

1. Fork this repository: on the repository page, click **Fork**.
2. In your fork, open the **Actions** tab, and enable workflows. The workflows only write to your fork.
3. You'll be editing file by file. If you need to create a new file, use the **Add File** button at the top of the interface.
4. For file edits, there is a pen at the top of each file, the shortcut for **Edit in Place** is `E`.

After making an edit you are asked if you want to commit and push the change you've made. Title the commit so you can return to it.

Then open the **Actions** tab of your fork to see the new workflow runs.

## Solutions

The exercise instructions contain both hints and solutions. You are kindly asked to attempt the problem yourself before copying the solution. This is meant to be there only so you do not get stuck!

## Repository

To change:

- `src/ci_cd/train.py`: trains the model and saves it to `model/`.
- `src/ci_cd/api.py`: serves the model with a web API.
- `Dockerfile`: builds the image that runs the training.
- `deployment.Dockerfile`: builds the image that serves the model.
- The CI configuration:
   - `.github/workflows/ci.yml`: checks the code, and trains the model on demand.
   - `.github/workflows/docker.yml`: builds the image on every push.
   - `.github/workflows/train-docker.yml`: trains the model in an image from the registry.
   - `.github/workflows/deploy.yml`: serves the model in a container, and checks that it answers.
   - `.gitlab-ci.yml`: the pipeline for GitLab CI/CD (if using GitLab).
- `tests/test_model.py`: checks the model accuracy.
- `tests/test_api.py`: checks the web API.

The other files are there to complete the repository (i.e. `uv.lock` for reproducibility, `.gitignore` to prevent committing local files, you have likely seen these before).

To see the pipelines/workflows made by this repository:

- **GitLab**: in your project, go to **Build -> Pipelines**.
- **GitHub**: in your repository, open the **Actions** tab.
