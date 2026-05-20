#!/usr/bin/env bash
set -euo pipefail

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
SERVER="${SERVER:-project6-tgbot}"
APP_DIR="${APP_DIR:-/opt/project_6_tgbot}"
SERVICE="${SERVICE:-project6-tgbot.service}"

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit or stash local changes before deploy." >&2
  git status --short >&2
  exit 1
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$BRANCH" ]]; then
  echo "Deploy expects branch '$BRANCH', but current branch is '$current_branch'." >&2
  exit 1
fi

git fetch "$REMOTE" "$BRANCH"
git merge --ff-only "$REMOTE/$BRANCH"
git push "$REMOTE" "HEAD:$BRANCH"

commit_sha="$(git rev-parse HEAD)"

ssh "$SERVER" "set -e
cd '$APP_DIR'
git -c safe.directory='$APP_DIR' fetch origin '$BRANCH'
git -c safe.directory='$APP_DIR' reset --hard '$commit_sha'
.venv/bin/python -m pip install -r requirements.txt
chown -R telegrambot:telegrambot '$APP_DIR'
systemctl restart '$SERVICE'
systemctl --no-pager --full status '$SERVICE' | sed -n '1,14p'
"

echo "Deployed $commit_sha to $SERVER:$APP_DIR"
