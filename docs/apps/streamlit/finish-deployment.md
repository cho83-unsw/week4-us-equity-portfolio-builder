# Finish Streamlit Deployment

Use this guide after `prepare-app-repo --push` has created and pushed the
clean private deploy repository.

## Week 2 Example Fields

If you created the standard Week 2 deploy repo, use these fields:

```text
Repository: your-github-username/week2-month-end-market-macro
Branch: main
Main file path: fins2026/week2/app/streamlit_app.py
Python version: 3.13
Secrets: none
```

If using `Paste GitHub URL`, paste the URL to the `.py` file:

```text
https://github.com/your-github-username/week2-month-end-market-macro/blob/main/fins2026/week2/app/streamlit_app.py
```

Do not paste only the repository root in that mode:

```text
https://github.com/your-github-username/week2-month-end-market-macro
```

## Deploy From Streamlit Cloud

1. Open `https://share.streamlit.io`.
2. Sign in with the GitHub account that owns the private deploy repo.
3. Click `Create app`.
4. Choose the option for an existing app or existing GitHub repository.
5. Prefer the interactive picker. Search for the repository name.
6. If the private repo is visible, select it and enter:
   - branch: `main`
   - main file path: `fins2026/week2/app/streamlit_app.py`
7. If the private repo is not visible, click `Paste GitHub URL` and paste the
   full `.py` file URL shown above.
8. Open `Advanced settings`.
9. Set Python to `3.13` where available.
10. Leave secrets empty for Week 2.
11. Click `Deploy`.

For a final project, replace the repository and entrypoint with the values
printed by `check-app-submission`.

## Private Repository Access

If Streamlit cannot see the private repo:

1. Open the Streamlit workspace/account menu.
2. Go to `Settings`.
3. Go to `Linked accounts`.
4. Under `Source control`, connect or reconnect GitHub.
5. Authorize the `Streamlit` GitHub OAuth app for private repositories.
6. If GitHub offers selected-repository access, include the private hand-in
   repo.
7. Return to `Deploy an app` and try the interactive picker again.

If the picker still does not list the repo, use `Paste GitHub URL` with the
full `.py` file URL.

## If Deploy Does Nothing

If clicking `Deploy` appears to do nothing:

1. Confirm the main file path or pasted URL points to the `.py` entrypoint.
2. Confirm the private GitHub repo is authorized in Streamlit linked accounts.
3. Clear the custom `App URL` field and let Streamlit generate a default URL.
4. Hard-refresh the browser or retry in a fresh browser session.
5. If the issue persists after reauthorization, check Streamlit app/account
   status or contact Streamlit support.

This is usually a Streamlit/GitHub authorization or form-validation issue, not
an app-code issue.

## Make The App Public

A private GitHub repo can produce a private Streamlit app by default. For
grading, the Streamlit app must be public/searchable.

After the app deploys:

1. Return to the Streamlit workspace page that lists your apps.
2. Find the deployed app row.
3. Click the three-dot menu on the far right of that row.
4. Click `Settings`.
5. In the left sidebar, click `Sharing`.
6. Under `Who can view this app`, open the dropdown.
7. Select `This app is public and searchable`.
8. Close the settings panel.

The GitHub repo can remain private if the teaching team has access. The
Streamlit app URL must be public/searchable.

Do not use the globe icon alone as proof that the app is public. Always verify
the `Sharing` setting and then test the app in an incognito browser.

## Validate Like A Grader

Open a private/incognito browser window and paste the public `streamlit.app`
URL.

The deployment is ready only if:

- the URL is not `localhost`
- the app loads without GitHub or Streamlit login
- fixture mode works
- the Week 2 data-source control, sample-period control, series selector, line
  chart, displayed-data table, and CSV download work
- no red deployment error appears
- the teaching team can access the GitHub repo if it remains private

Record:

```text
Public Streamlit app URL:
GitHub repo URL:
Branch:
Entrypoint:
Final commit hash:
```

## Common Error: ModuleNotFoundError

Nested app entrypoints need to make the repository root importable before
importing repo-local packages such as `fintools`.

The required pattern is:

```python
import sys
from pathlib import Path

REPO_ROOT = next(
    (
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "fintools").is_dir()
    ),
    Path(__file__).resolve().parents[2],
)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

Place this before imports from repo-local packages.
