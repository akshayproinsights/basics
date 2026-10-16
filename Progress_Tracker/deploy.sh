#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  deploy.sh  —  Sync → GitHub → Firebase  in one command
#  Usage:  ./deploy.sh
#          ./deploy.sh "your commit message"
# ─────────────────────────────────────────────────────────────

set -e  # stop on any error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE="$SCRIPT_DIR/progress_Tracker.html"
TARGET="$SCRIPT_DIR/index.html"

# ── colours ──────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✔  $1${NC}"; }
info() { echo -e "${YELLOW}▸  $1${NC}"; }
err()  { echo -e "${RED}✖  $1${NC}"; exit 1; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Progress Tracker — Deploy Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. Sync progress_Tracker.html → index.html ───────────────
info "Syncing progress_Tracker.html → index.html..."
cp "$SOURCE" "$TARGET"
ok "index.html updated ($(wc -l < "$TARGET") lines)"

# ── 2. Git commit & push ──────────────────────────────────────
info "Committing to GitHub..."
cd "$REPO_ROOT"

git add Progress_Tracker/progress_Tracker.html Progress_Tracker/index.html

# Use provided message or auto-generate one with timestamp
COMMIT_MSG="${1:-"chore: deploy tracker update $(date '+%Y-%m-%d %H:%M')"}"

if git diff --cached --quiet; then
  info "Nothing new to commit — files already up to date."
else
  git commit -m "$COMMIT_MSG"
  git push origin main
  ok "Pushed to GitHub ($(git rev-parse --short HEAD))"
fi

# ── 3. Firebase deploy ────────────────────────────────────────
info "Deploying to Firebase Hosting..."
cd "$SCRIPT_DIR"
firebase deploy --only hosting --project ai-engineer-tracker-44207

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ok "All done!"
echo ""
echo "   🌐  https://ai-engineer-tracker-44207.web.app"
echo "   📦  https://github.com/akshayproinsights/basics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
