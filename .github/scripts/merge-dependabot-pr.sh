#!/usr/bin/env bash
# Move a Dependabot PR onto develop and set it to merge once the required CI
# checks (Tests, Docker build) pass. Branch protection on develop enforces them.
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

# GitHub works out mergeability in the background, so give it a moment.
for _ in 1 2 3 4 5 6; do
  mergeable=$(gh pr view "$pr" --json mergeable --jq .mergeable)
  [[ "$mergeable" != "UNKNOWN" ]] && break
  sleep 5
done
head_sha=$(gh pr view "$pr" --json headRefOid --jq .headRefOid)

# A rebase onto develop fixes conflicts, and it also gives older PRs (opened
# before CI existed) a new commit that CI runs on. Only the sweep checks for
# missing CI: on a PR event, CI is starting alongside this run.
ci_runs=unchecked
if [[ "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
  ci_runs=$(gh api "repos/{owner}/{repo}/commits/$head_sha/check-runs?check_name=Tests" --jq .total_count)
fi
if [[ "$mergeable" == "CONFLICTING" || "$ci_runs" == "0" ]]; then
  echo "PR #$pr needs a rebase (mergeable=$mergeable, CI runs=$ci_runs); asking Dependabot."
  gh pr comment "$pr" --body "@dependabot rebase"
  exit 0
fi

# --match-head-commit means only the commit CI checked gets merged. If the
# checks have already passed, auto-merge can't be turned on, so merge directly.
if gh pr merge "$pr" --auto --squash --match-head-commit "$head_sha" 2>&1; then
  echo "Auto-merge enabled for PR #$pr; GitHub merges it once CI passes."
else
  gh pr merge "$pr" --squash --match-head-commit "$head_sha"
  echo "Merged PR #$pr into $target"
fi
