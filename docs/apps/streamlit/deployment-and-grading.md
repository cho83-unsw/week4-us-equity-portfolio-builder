# Deployment And Grading

Default deployment target: Streamlit Community Cloud.

Students submit:

- public Streamlit app URL
- GitHub repo URL that the teaching team can access
- branch
- entrypoint file path
- final commit hash
- short README explaining data, insight, and local run command

The app must load for the grader in an incognito browser.

Local testing is different from deployment: `localhost` works only while the
student's own Streamlit process is running. For grading, submit the public
Streamlit Community Cloud URL, not a `localhost` URL.

## Deployment Checklist

1. Commit the app code, data fixture, and requirements.
2. Commit `.streamlit/config.toml`, but do not commit `.streamlit/secrets.toml`.
3. Run `python tools/workflow.py check-app-submission --target projects/my_project`
   and resolve blocking issues.
4. Push to the student's private GitHub repository.
5. In Streamlit Community Cloud, create an app from the repository.
6. Set the branch and entrypoint path, for example:
   `projects/my_project/app/streamlit_app.py`.
7. Select the course Python version where available.
8. Paste secrets in Advanced settings only if the app needs them.
9. Make the Streamlit app public for grading: from the Streamlit workspace app
   list, click the app row's three-dot menu, open `Settings`, go to `Sharing`,
   and set `Who can view this app` to `This app is public and searchable`.
10. Give the teaching team GitHub repo access by making the repo public or by
   adding graders as collaborators before the deadline.
11. Open the deployed URL in an incognito browser.

Use `finish-deployment.md` for the click-by-click browser workflow, including
private GitHub authorization, `Paste GitHub URL`, public app sharing, and
incognito validation.

## Grading Checks

- The URL is public and loads.
- The GitHub repo is accessible to the teaching team.
- The app has a clear question and insight.
- Data sources and transformations are documented.
- The app is reproducible from GitHub.
- Controls work without crashing the app.
- Charts are readable and labels are publication-quality.
- Forecasts include backtest or caveat context.
