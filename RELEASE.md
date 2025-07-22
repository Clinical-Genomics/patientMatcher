# Instructions to release a new release

1. Create a release branch with the release name, e.g. `release_2.0.0` and checkout

    ```bash
    git checkout -b release_2.0.0
    ```

1. Update version to, e.g. 2.0.0

   - in `pyproject.toml`

1. Upgrade dependencies that are not frozen to their latest compatible version e.g.
   ```bash
   uv lock --upgrade
   git add uv.lock
   git commit -m 'Upgrade dependencies'
   ```

1. Make sure CHANGELOG.md is up to date for the release

1. Commit changes, push to github and create a pull request

    ```bash
    git add -u
    git commit -m "Release version 2.0.0"
    git push
    ```

1. On github click "Create pull request"

1. After getting the pull request approved by a reviewer merge it to main.

1. Draft a new release on GitHub, add some text - e.g. an abbreviated CHANGELOG - and release.
This adds a version tag, builds and submits to PyPi.