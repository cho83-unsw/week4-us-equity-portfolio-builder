# Streamlit App Student Quickstart

Use this page when you want to turn coursework analysis into a public
Streamlit app without guessing through the deployment steps.

## Week 0 Fast Path: Rehearse The Week 2 Deploy

If you do not want to think about the Week 2 economics yet, that is fine.
Week 0 is about the workflow, not the macro content.

1. Run the existing app locally:

```bash
streamlit run fins2026/week2/app/streamlit_app.py
```

2. If `http://localhost:8501` opens, paste this into your agent:

```text
Help me deploy the Week 2 Streamlit app using
docs/apps/streamlit/student-quickstart.md.

Target folder: fins2026/week2
Entrypoint: fins2026/week2/app/streamlit_app.py
Deploy repo name: week2-month-end-market-macro

I do not need help with the economics yet.
I only need to run the existing app, prepare the clean deploy repo,
push it to GitHub, and give me the exact Streamlit Cloud fields.
If deployment fails, diagnose the error and fix it.
```

3. The agent should run the readiness check and then create the clean deploy
   repo:

```bash
python tools/workflow.py check-app-submission --target fins2026/week2 --entrypoint fins2026/week2/app/streamlit_app.py
python tools/workflow.py prepare-app-repo --source fins2026/week2 --dest ../week2-month-end-market-macro --repo week2-month-end-market-macro --entrypoint fins2026/week2/app/streamlit_app.py --push
```

4. Deploy on Streamlit Community Cloud with:

```text
Repository: your-github-username/week2-month-end-market-macro
Branch: main
Main file path: fins2026/week2/app/streamlit_app.py
Python version: 3.13
Secrets: none
```

5. Make the app public and test the `streamlit.app` URL in an incognito
   browser.

## The Big Picture

You will work locally first, then deploy from GitHub:

1. Build and run the app on your own computer.
2. Commit the working app.
3. Check that the app is ready for deployment.
4. Push a clean private deploy repo.
5. Deploy that repo on Streamlit Community Cloud.
6. Make the Streamlit app public.
7. Test the public URL like a grader.

## Step 1: Run The App Locally

Open a terminal at the repo root. For the Week 2 example, run:

```bash
streamlit run fins2026/week2/app/streamlit_app.py
```

For your own project, replace the path with your app path, for example:

```bash
streamlit run projects/my_project/app/streamlit_app.py
```

Streamlit will open a local browser URL such as:

```text
http://localhost:8501
```

Important: `localhost` is not a public website. It only works on your computer
while the Streamlit command is still running.

## Step 2: Keep The Local Server Running

Keep the terminal, PowerShell tab, or PyCharm Run pane open while you use the
local app.

If you close that window, the app stops. The browser may then say it cannot
reach `localhost`. That is not a deployment problem; it means the local
Streamlit server stopped.

On macOS, a Watchdog or Xcode Command Line Tools message is usually a
performance suggestion for faster reloads, not a fatal error.

When you are finished testing locally, stop Streamlit with `Ctrl+C` in the
terminal.

## Step 3: Check The App Like A User

Before deployment, confirm:

- the app opens without a Python traceback
- every sidebar control works
- controls are near the view they affect
- if the app uses tabs, every tab renders
- important controls can be shared through the app URL
- the app shows source, sample span, observation count, and missing values
- charts have readable labels
- metrics and table columns include units where needed
- composite scores say whether higher values are good or bad, explain the
  comparison window, and show a current or recent value
- percentiles are interpreted in plain English
- visible text sounds like a professional product, not notes about how the app
  is built
- time-series charts have useful hover labels and range controls
- time-series lines do not jump diagonally across the chart because dates were
  plotted out of order
- tables do not show raw names such as `absolute_error`
- if the app includes forecasts, they explain whether they model levels,
  changes, growth, or skip a context series such as VIX
- long forecast-target names or formulas do not appear as oversized metric
  values
- useful data/model outputs can be downloaded as CSV files
- live data either works or falls back to fixture data
- if the app includes a Method section, it explains the data, model,
  backtest, and caveats clearly

For the Week 2 intro app specifically, also confirm that the series selector,
sample-period control, line chart, displayed-data table, and CSV download all
work cleanly.

For the full quality checklist, use `publication-grade-apps.md`.

## Step 4: Commit Your Work

Commit the latest app code before deployment. The public Streamlit app deploys
from GitHub, not from uncommitted files on your computer.

Do not commit secrets, `.streamlit/secrets.toml`, `.env`, `.venv/`, local paths
such as `C:\Users\...` or `/Users/...`, or private raw data.

If this is your final project repo, add the instructor GitHub account as a
collaborator as soon as the private repo exists. The helper files already carry
the deployment metadata; just keep the repo URL and access details current as
you set the repo up.

## Step 5: Run The Readiness Check

From the repo root, run the deployment readiness check.

Week 2 example:

```bash
python tools/workflow.py check-app-submission --target fins2026/week2 --entrypoint fins2026/week2/app/streamlit_app.py
```

Project example:

```bash
python tools/workflow.py check-app-submission --target projects/my_project
```

If the command says `BLOCKED`, fix the blocking issue before deployment.

The checker uses the target path, entrypoint, and Git state to print the exact
Streamlit Cloud fields. If you keep an optional `submission.json` file for
deployment metadata, do not let it contradict the real repository.

## Step 6: Create The Private Hand-In Repo

If you are working inside the course repo, create a clean private deploy repo
with `prepare-app-repo`.

Week 2 example:

```bash
python tools/workflow.py prepare-app-repo --source fins2026/week2 --dest ../week2-month-end-market-macro --repo week2-month-end-market-macro --entrypoint fins2026/week2/app/streamlit_app.py --push
```

Project example:

```bash
python tools/workflow.py prepare-app-repo --source projects/my_project --dest ../my_project_handin --repo my_project_handin --push
```

This creates a minimal deployable repo and pushes it to GitHub. It does not
push the course repo's `origin`.

The prepared repo also includes `.github/workflows/submission-check.yml`, so
every push runs the same submission gate in GitHub Actions.

## Step 7: Deploy On Streamlit Community Cloud

Open:

```text
https://share.streamlit.io
```

Create a new app from GitHub. Use the values printed by
`check-app-submission`.

For Week 2, the values are:

```text
Repository: your deploy repo, for example `your-github-username/week2-month-end-market-macro`
Branch: main
Main file path: fins2026/week2/app/streamlit_app.py
Python version: 3.13
Secrets: none
```

For a project, the main file path is usually:

```text
projects/my_project/app/streamlit_app.py
```

If your app uses secrets, do not commit them. Paste secrets into Streamlit
Cloud's Advanced settings.

## Step 8: If The Private Repo Is Missing

Sometimes Streamlit does not show private GitHub repos in the picker.

Fix it by authorizing GitHub private repo access:

1. Open Streamlit account settings.
2. Go to `Linked accounts`.
3. Reconnect GitHub under source control.
4. Allow Streamlit to access private repositories.
5. Return to app deployment.

If the picker still does not show the repo, use `Paste GitHub URL`.

When using `Paste GitHub URL`, paste the `.py` file URL, not the repo root.

Correct shape:

```text
https://github.com/username/repo/blob/main/projects/my_project/app/streamlit_app.py
```

Wrong shape:

```text
https://github.com/username/repo
```

## Step 9: Make The App Public

Deploying from a private GitHub repo can still create a private Streamlit app.
For grading, the Streamlit app must be public.

After deployment:

1. Return to the Streamlit page that lists your apps.
2. Find your app row.
3. Click the three-dot menu on the right side of the row.
4. Click `Settings`.
5. Click `Sharing`.
6. Under `Who can view this app`, choose
   `This app is public and searchable`.

The GitHub repo can remain private if the teaching team has access. The
Streamlit app URL must be public.

## Step 10: Test Like A Grader

Open a private or incognito browser window. Paste the public `streamlit.app`
URL.

The app is ready only if:

- it is not a `localhost` URL
- it loads without GitHub or Streamlit login
- controls work
- tabs render
- no red deployment error appears
- the GitHub repo is accessible to the teaching team

## What To Record

Record:

- Public Streamlit app URL
- GitHub repository URL that the teaching team can access
- Branch, usually `main`
- Entrypoint path, for example `projects/my_project/app/streamlit_app.py`
- Final commit hash
- the deployment metadata updated with the final repo URL, public app URL, and
  teaching-team access mode

## Copy-Paste Prompt For Your AI Assistant

```text
Help me deploy the Week 2 Streamlit app using
docs/apps/streamlit/student-quickstart.md.

Target folder: fins2026/week2
Entrypoint: fins2026/week2/app/streamlit_app.py
Deploy repo name: week2-month-end-market-macro

I do not need help with the economics yet.
I only need to run the existing app, prepare the clean deploy repo,
push it to GitHub, and give me the exact Streamlit Cloud fields.
If deployment fails, diagnose the error and fix it.
```

## Quick Gotcha List

- `localhost` is only your computer.
- Closing the Streamlit terminal stops the local app.
- GitHub repo privacy and Streamlit app privacy are separate settings.
- The Streamlit app must be public for grading.
- `Paste GitHub URL` needs the `.py` file URL.
- The private GitHub repo must be visible to the teaching team by the deadline.
- The deployment metadata file must match the final repo and deployed app state.
- Do not commit secrets.
- Do not commit `.venv/`.
- Do not commit local absolute paths.
- Live APIs can fail; include fixture or fallback data.
- Do not forecast levels just because the dataframe contains levels.
