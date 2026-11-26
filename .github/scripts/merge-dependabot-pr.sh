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

# Dependabot rebases conflicting PRs itself (it ignores "@dependabot rebase"
# from this workflow's bot account, so asking doesn't help).
if [[ "$mergeable" == "CONFLICTING" ]]; then
  echo "PR #$pr conflicts with $target; leaving it for Dependabot to rebase."
  exit 0
fi

# Older PRs (opened before CI existed) have no CI run, so required checks
# would never pass. Only the sweep checks this: on a PR event, CI is starting
# alongside this run.
if [[ "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
  ci_runs=$(gh api "repos/{owner}/{repo}/commits/$head_sha/check-runs?check_name=Tests" --jq .total_count)
  if [[ "$ci_runs" == "0" ]]; then
    head_ref=$(gh pr view "$pr" --json headRefName --jq .headRefName)
    # Merge develop into the PR branch so it has the CI workflow and is tested
    # against current develop. Fails harmlessly if it's already up to date.
    echo "PR #$pr has no CI run; updating its branch from $target."
    if gh api -X PUT "repos/{owner}/{repo}/pulls/$pr/update-branch" \
         -f expected_head_sha="$head_sha" --silent; then
      for _ in $(seq 1 12); do
        new_sha=$(gh pr view "$pr" --json headRefOid --jq .headRefOid)
        [[ "$new_sha" != "$head_sha" ]] && break
        sleep 5
      done
      if [[ "$new_sha" == "$head_sha" ]]; then
        echo "PR #$pr branch update hasn't shown up yet; the next sweep will retry."
        exit 0
      fi
      head_sha="$new_sha"
    fi
    # Commits pushed with GITHUB_TOKEN don't start workflows, but a manual
    # dispatch does, and its checks count for the PR's head commit.
    gh workflow run ci.yml --ref "$head_ref"
    echo "Started CI on $head_ref ($head_sha)."
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
