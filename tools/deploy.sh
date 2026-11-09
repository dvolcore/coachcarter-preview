#!/bin/zsh
# Rebuild and publish site/ to the gh-pages branch (GitHub Pages serves that branch).
set -e
cd "$(dirname "$0")/.."
python3 tools/build.py
git add -A && git commit -q -m "${1:-Update preview}" || true
git push -q origin main
git push -q origin "$(git subtree split --prefix site main)":refs/heads/gh-pages --force
echo "Deployed: https://dvolcore.github.io/coachcarter-preview/"
