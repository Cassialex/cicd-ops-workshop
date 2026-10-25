# Exercise 1 — Run and explore images

**Goal:** see what a base image contains, and how a container differs from its
image.

## 1.a Compare two base images

The official Python image comes in several variants. Compare the default one
with the slim one.

1. Pull both images:

   ```sh
   docker pull python:3.12
   docker pull python:3.12-slim
   ```

2. List them and compare the `SIZE` column:

   ```sh
   docker images python
   ```

3. Open a shell in each image and check which tools exist:

   ```sh
   docker run --rm -it python:3.12 bash
   ```

   Inside the container, try `gcc --version`, `git --version` and
   `curl --version`. Type `exit` to leave. Repeat with `python:3.12-slim`.

4. Start a container in the background, then stop it and remove it:

   ```sh
   docker run -d --name py-slim python:3.12-slim sleep infinity
   docker ps
   docker stop py-slim
   docker ps -a
   docker rm py-slim
   ```

<details>
<summary>Hint: what do these flags do?</summary>

- `--rm` removes the container when it stops.
- `-it` connects your terminal to the container, so you can type in its shell.
- `-d` runs the container in the background. `sleep infinity` keeps it running.
- `--name` gives the container a name to use in the next commands.
- `docker ps` lists the running containers. `docker ps -a` also lists the
  stopped ones.

</details>

<details>
<summary>Hint: what should I notice?</summary>

- The default image is several times larger than the slim one.
- The default image has compilers and build tools, such as `gcc` and `git`.
  The slim one doesn't.
- A stopped container stays on your disk until you remove it.

</details>

**Done when:** you can say which tools each image has, and you can start, stop
and remove a container.

## 1.b Change a running container

1. Start a container in the background and install a package in it:

   ```sh
   docker run -d --name scratch python:3.12-slim sleep infinity
   docker exec scratch pip install pandas
   docker exec scratch python -c "import pandas; print(pandas.__version__)"
   ```

2. Stop the container, start it again, and check the import:

   ```sh
   docker stop scratch
   docker start scratch
   docker exec scratch python -c "import pandas; print(pandas.__version__)"
   ```

3. Remove the container, start a new one from the same image, and check the
   import:

   ```sh
   docker rm -f scratch
   docker run -d --name scratch python:3.12-slim sleep infinity
   docker exec scratch python -c "import pandas"
   ```

4. Clean up with `docker rm -f scratch`.

<details>
<summary>Hint: why did the package survive step 2, but not step 3?</summary>

Each container writes its changes to its own layer, on top of the image. That
layer lives as long as the container. Stopping and starting keeps it. Removing
the container deletes it, and a new container starts from the unchanged image.

</details>

**Done when:** you can explain when an install inside a container survives, and
when it doesn't.

## Conclusion

A base image is a named set of tools: an operating system, Python, and, for the
default image, build tools. Changes made inside a container stay in
that container.

*Topics: `docker pull`, `docker images`, `docker run` (`--rm`, `-it`, `-d`,
`--name`), `docker ps`, `docker stop`, `docker start`, `docker rm`,
`docker exec`.*