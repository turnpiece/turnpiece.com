#!/usr/bin/env bash
# Move a Dependabot PR onto develop, test it merged with develop, and merge it.
# Usage: merge-dependabot-pr.sh <pr-number>
# Needs GH_TOKEN with contents:write and pull-requests:write.
set -euo pipefail

pr="$1"
target=develop

author=$(gh pr view "$pr" --json author --jq .author.login)
if [[ "$author" != "app/dependabot" && "$author" != "dependabot[bot]" ]]; then
  echo "PR #$pr is by $author, not Dependabot; skipping."
  exit 0
fi

# Major version bumps get a human look. Check the title and, for grouped PRs,
# each "Updates `pkg` from X to Y" line in the body.
bumps=$( { gh pr view "$pr" --json title --jq .title
           gh pr view "$pr" --json body --jq .body | grep -E '^(Updates|Bumps) ' || true; } )
while IFS= read -r line; do
  if [[ "$line" =~ from\ v?([0-9]+)[^\ ]*\ to\ v?([0-9]+) ]] \
     && [[ "${BASH_REMATCH[1]}" != "${BASH_REMATCH[2]}" ]]; then
    echo "PR #$pr has a major version bump ($line); leaving it for review."
    exit 0
  fi
done <<< "$bumps"

base=$(gh pr view "$pr" --json baseRefName --jq .baseRefName)
if [[ "$base" != "$target" ]]; then
  echo "Retargeting PR #$pr from $base to $target"
  gh pr edit "$pr" --base "$target"
fi

# Test the PR as it would look once merged into the latest develop.
git fetch --quiet origin "$target" "pull/$pr/head"
head_sha=$(git rev-parse FETCH_HEAD)
git checkout --quiet --detach "origin/$target"
if ! git -c user.name=ci -c user.email=ci@localhost merge --quiet --no-edit "$head_sha"; then
  git merge --abort
  echo "PR #$pr conflicts with $target; asking Dependabot to rebase."
  gh pr comment "$pr" --body "@dependabot rebase"
  exit 0
fi

pip install --quiet -r requirements.txt
(cd theme && npm ci --no-audit --no-fund && npm run build-css)
python manage.py collectstatic --noinput >/dev/null
python manage.py test

# --match-head-commit guards against merging something other than what was tested.
# Dependabot deletes its own branch once the PR is merged.
gh pr merge "$pr" --squash --match-head-commit "$head_sha"
echo "Merged PR #$pr into $target"
