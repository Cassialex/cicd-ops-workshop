# Exercise 2 — Build the project's image

**Goal:** read the project's `Dockerfile`, build it, and see how Docker reuses
layers between builds.

## 2.a Read and build

1. Open the `Dockerfile` at the root of the repo. For each line, say what it
   does and why it is there.

   <details>
   <summary>Hint: the instructions</summary>

   | Instruction | What it does |
   | ----------- | ------------ |
   | `FROM` | The base image to start from |
   | `WORKDIR` | The folder where the next instructions run, created if needed |
   | `COPY` | Copies files from your machine into the image |
   | `RUN` | Runs a command during the build |
   | `ENV` | Sets an environment variable in the image |
   | `CMD` | The command a container runs when it starts |

   </details>

2. Build the image from the root of the repo:

   ```sh
   docker build -t iris-classifier .
   ```

   The final `.` is the build context: the folder Docker sends to the build,
   and the only one `COPY` can read from.

3. Run the training in a container:

   ```sh
   docker run --rm iris-classifier
   ```

   It prints the settings of the model and the accuracy.

**Done when:** the container prints the accuracy, and you can explain each line
of the `Dockerfile`.

## 2.b Rebuild after a code change

1. Change something in `src/ci_cd/train.py`, e.g. `TEST_SIZE`.
2. Rebuild the image. Look at the build output and its duration.

<details>
<summary>Hint: why does the install run again?</summary>

Docker stores each layer in a cache. It reuses a layer while its instruction
and its inputs don't change. `COPY . .` copies `train.py`, so its layer
changes. When a layer changes, Docker rebuilds it and every layer after it,
including `pip install`.

</details>

**Done when:** you can say why a one-line code change reinstalls every
dependency.

## 2.c Change the order

1. In the `Dockerfile`, copy `requirements.txt` on its own and install the
   dependencies, before you copy the rest of the code:

   ```dockerfile
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   ```

2. Rebuild, change `train.py` again, and rebuild once more.
3. Compare with 2.b: which steps ran again, and how long did the build take?

<details>
<summary>Hint: why is it fast now?</summary>

The install only depends on `requirements.txt`, which didn't change. Its step
says `CACHED`, and only `COPY . .` runs again. Put the instructions that change
least at the top.

</details>

> To rebuild every layer without the cache, add `--no-cache`:
> `docker build --no-cache -t iris-classifier .`

**Done when:** you can explain why `requirements.txt` is copied on its own,
before the rest of the code.

## 2.d Settings and folders (if time)

1. Run the training with another number of trees, without rebuilding:

   ```sh
   docker run --rm -e N_ESTIMATORS=50 iris-classifier
   ```

2. Check your `model/` folder: no new model is there. Run the training again,
   with the `model/` folder mounted into the container:

   ```sh
   docker run --rm -e N_ESTIMATORS=50 -v ./model:/app/model iris-classifier
   ```

<details>
<summary>Hint: what do `-e` and `-v` do?</summary>

- `-e NAME=value` sets an environment variable in the container. It replaces
  the value from the `Dockerfile`'s `ENV`.
- `-v host:container` mounts a folder from your machine into the container.
  The container writes `model.pkl` to `/app/model`, which is your `model/`
  folder. Without `-v`, the file stays in the container, and `--rm` deletes it.

</details>

**Done when:** `model/model.pkl` and `model/metrics.json` appear on your
machine.

## Conclusion

A `Dockerfile` lists the steps that turn a base image into your image. Docker
caches each step, and reuses it until the step or its inputs change. In CI,
every job starts on a clean machine, so the image has to be stored in a
registry to be used by later jobs. That is the next exercise.

*Topics: `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `CMD`, `docker build -t`,
the build context, the layer cache, `--no-cache`, `docker run -e` and `-v`.*
