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

# This workflow never pushes to Dependabot's branches: once anyone else has
# pushed, Dependabot stops rebasing the PR, and CI on bot pushes needs manual
# approval. Anything stuck is flagged for a person instead.

# Dependabot rebases conflicting PRs itself.
if [[ "$mergeable" == "CONFLICTING" ]]; then
  echo "PR #$pr conflicts with $target; leaving it for Dependabot to rebase."
  exit 0
fi

# A PR with no CI run can never pass the required checks. Dependabot only
# takes commands from people with push access, so ask for one. Only the sweep
# checks this: on a PR event, CI is starting alongside this run.
if [[ "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
  ci_runs=$(gh api "repos/{owner}/{repo}/commits/$head_sha/check-runs?check_name=Tests" --jq .total_count)
  if [[ "$ci_runs" == "0" ]]; then
    echo "::warning::PR #$pr has never had a CI run. Comment \"@dependabot recreate\" on it to rebuild it so CI runs."
    exit 0
  fi
fi

# --match-head-commit means only the commit CI checked gets merged. If the
# checks have already passed, auto-merge can't be turned on, so merge directly.
if gh pr merge "$pr" --auto --squash --match-head-commit "$head_sha" 2>&1; then
  echo "Auto-merge enabled for PR #$pr; GitHub merges it once CI passes."
else
  gh pr merge "$pr" --squash --match-head-commit "$head_sha"
  echo "Merged PR #$pr into $target"
fi
