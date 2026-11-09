#!/bin/zsh
# Rebuild and publish site/ to the gh-pages branch (GitHub Pages serves that branch).
set -e
cd "$(dirname "$0")/.."
python3 tools/build.py
git add -A && git commit -q -m "${1:-Update preview}" || true
git fetch -q origin && git rebase -q origin/main   # never overwrite other sessions
python3 tools/build.py >/dev/null && git add -A && git commit -q -m "Rebuild after merge" || true
git push -q origin main
git push -q --force-with-lease origin "$(git subtree split --prefix site main)":refs/heads/gh-pages  # gh-pages is generated from main
echo "Deployed: https://dvolcore.github.io/coachcarter-preview/"
