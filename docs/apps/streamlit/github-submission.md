# GitHub And Streamlit Submission

Use this workflow for final project apps unless the instructor gives different
instructions.

## Default Project Repo Model

Students should use a private, student-owned GitHub repository while developing
their project.

This is different from local development:

- Local work happens in PyCharm and only runs on the student's computer.
- GitHub stores commits, backs up work, and gives the grader access to code.
- Streamlit Community Cloud hosts the public app URL used for grading.

Do not wait until the end to use GitHub. Commit locally and push regularly to a
private GitHub repository so there is a history of the work and a backup if the
computer fails.

## Recommended Mechanics

1. Create a private GitHub repository under the student's own GitHub account.
2. In class, add the instructor GitHub account as a collaborator immediately.
   Add marker accounts at the same time if the course is grading directly from
   student repos.
3. Clone the repository locally.
4. Work locally in PyCharm.
5. Commit and push regularly.
6. If the repo carries an optional `submission.json` metadata file, keep it
   aligned with the repo URL, entrypoint, app visibility, and teaching-team
   access mode.
7. Run the app locally with `streamlit run app/streamlit_app.py`.
8. Run `python tools/workflow.py check-app-submission --target .` from the repo
   root and fix blocking issues.
9. Near hand-in, deploy the app from GitHub to Streamlit Community Cloud.
10. Make the Streamlit app public for grading. From the Streamlit app list,
   click the app row's three-dot menu, open `Settings`, go to `Sharing`, and
   set `Who can view this app` to `This app is public and searchable`.
11. Give the teaching team access to the GitHub repository, either by making the
   repo public at hand-in or by adding the grader as a collaborator before the
   deadline.

Student-owned repositories are the default for final projects because the
student has admin permission on the repo. That makes Streamlit Community Cloud
deployment simpler than deploying from a private organization-owned classroom
repository.

When a student has been working inside the shared course repo and needs a clean
deploy repository, use:

```bash
python tools/workflow.py prepare-app-repo --source projects/my_project --dest ../my_project_handin --repo my_project_handin --push
```

The command creates a minimal deployable bundle and never pushes the course
repo's `origin`.

After the private repo is pushed, finish the browser-only Streamlit deployment
steps with `docs/apps/streamlit/finish-deployment.md`.

The prepared bundle also includes
`.github/workflows/submission-check.yml`. Every push in the deploy repo runs
the same readiness gate used locally by `check-app-submission`.

## Submission Package

Submit all of the following:

- public Streamlit app URL
- GitHub repository URL that the teaching team can access
- branch name, normally `main`
- app entrypoint path, normally `app/streamlit_app.py`
- final commit hash
- short README explaining the data, insight, local run command, and deployment
  path
- if you keep an optional `submission.json`, its repo URL, entrypoint,
  visibility, and teaching-team access details match the actual hand-in state

The Streamlit app must load in an incognito browser. A `localhost` URL is not a
valid submission because it only works on the student's own computer while the
local Streamlit process is running.

## Privacy And Access

The GitHub repository may stay private during development. At hand-in, the
teaching team must be able to inspect the exact code used for the public app.

Acceptable repo-access choices:

- make the repo public at hand-in
- keep the repo private and add the instructor or TA GitHub accounts as
  collaborators before the deadline

For student-owned personal repositories, collaborator access gives the teaching
team read/write access but does not transfer ownership. Archive or clone the
repos at the deadline if the course needs a permanent grading copy.

Do not commit secrets, API keys, passwords, `.streamlit/secrets.toml`, `.env`,
large private datasets, local absolute paths, or `.venv/`.

## Common Failure Modes

- The app works at `localhost:8501`, but the grader cannot open it. Fix: deploy
  to Streamlit Community Cloud and submit the public `streamlit.app` URL.
- `check-app-submission` reports `BLOCKED`. Fix every blocking issue before
  deploying or handing in.
- The private repo does not appear in Streamlit's picker. Fix: authorize
  private repo access under Streamlit `Settings` -> `Linked accounts`, or use
  `Paste GitHub URL` with the full `.py` file URL.
- The `Paste GitHub URL` field rejects the repo. Fix: paste the URL to the
  `.py` entrypoint file, not the repository root.
- Streamlit deploys an old version. Fix: commit and push the latest code, then
  check the deployed app logs.
- Streamlit cannot find the app file. Fix: use the exact entrypoint path from
  the repo root, for example `app/streamlit_app.py`.
- Streamlit raises `ModuleNotFoundError` for a repo-local package. Fix: add the
  repo-root `sys.path` bootstrap before local package imports, or use the app
  scaffold generated by this repo.
- The app fails after deployment because a file path starts with `C:\Users\` or
  `/Users/`. Fix: use repo-relative paths such as
  `Path(__file__).resolve().parents[1] / "data" / "file.csv"`.
- The app needs a secret locally. Fix: keep local secrets in
  `.streamlit/secrets.toml`, never commit that file, and paste required secrets
  into Streamlit Community Cloud settings.
- The repo is private and the teaching team cannot see it. Fix: add grader
  collaborators before the deadline or make the repo public.
