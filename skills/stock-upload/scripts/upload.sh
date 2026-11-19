#!/usr/bin/env bash
# Back up a batch to Google Drive and upload final/*.jpg to Adobe Stock via rclone.
# Usage: upload.sh BATCH_DIR [--dry-run] [--drive-only] [--adobe-only]
set -euo pipefail

BATCH="${1:?usage: upload.sh BATCH_DIR [--dry-run] [--drive-only] [--adobe-only]}"; shift
DRY=""; DO_DRIVE=1; DO_ADOBE=1
for a in "$@"; do
  case "$a" in
    --dry-run) DRY="--dry-run" ;;
    --drive-only) DO_ADOBE=0 ;;
    --adobe-only) DO_DRIVE=0 ;;
    *) echo "unknown option $a"; exit 1 ;;
  esac
done

DRIVE_REMOTE="${DRIVE_REMOTE:-gdrive}"
DRIVE_FOLDER="${DRIVE_FOLDER:-microstock}"
ADOBE_REMOTE="${ADOBE_REMOTE:-adobestock}"
NAME="$(basename "$(cd "$BATCH" && pwd)")"
LOG="$BATCH/upload.log"

command -v rclone >/dev/null || { echo "rclone not installed: brew install rclone"; exit 1; }
ls "$BATCH"/final/*.jpg >/dev/null 2>&1 || { echo "No JPEGs in $BATCH/final — run prepare_images.py first"; exit 1; }
[ -f "$BATCH/adobe_stock.csv" ] || echo "⚠ $BATCH/adobe_stock.csv missing — run build_csv.py before submitting in the portal"

has_remote() { rclone listremotes | grep -qx "$1:"; }
log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

if [ $DO_DRIVE = 1 ]; then
  if has_remote "$DRIVE_REMOTE"; then
    log "Drive: $BATCH → $DRIVE_REMOTE:$DRIVE_FOLDER/$NAME $DRY"
    rclone copy $DRY --progress --exclude ".env" --exclude "raw/**" --exclude "*.part" \
      "$BATCH" "$DRIVE_REMOTE:$DRIVE_FOLDER/$NAME"
    [ -z "$DRY" ] && log "Drive link: run  rclone link $DRIVE_REMOTE:$DRIVE_FOLDER/$NAME  to share"
  else
    log "Drive skipped: rclone remote '$DRIVE_REMOTE' not configured"
  fi
fi

if [ $DO_ADOBE = 1 ]; then
  if has_remote "$ADOBE_REMOTE"; then
    COUNT=$(ls "$BATCH"/final/*.jpg | wc -l | tr -d ' ')
    log "Adobe SFTP: $COUNT JPEGs → $ADOBE_REMOTE: $DRY"
    rclone copy $DRY --progress --include "*.jpg" --transfers 4 "$BATCH/final" "$ADOBE_REMOTE:"
    [ -z "$DRY" ] && log "Next: portal → Upload CSV (adobe_stock.csv) → tick generative AI box → Submit"
  else
    log "Adobe skipped: rclone remote '$ADOBE_REMOTE' not configured (see SKILL.md setup)"
  fi
fi
