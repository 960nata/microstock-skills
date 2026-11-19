---
name: stock-upload
description: Back up a finished stock batch to Google Drive and upload its JPEGs to Adobe Stock over SFTP with rclone, then guide the CSV metadata import and the AI disclosure checkboxes in the contributor portal. Use when the user wants to upload images to Adobe Stock, sync a batch to Google Drive, download/share a batch, or set up Adobe Stock SFTP.
---

# Upload: Google Drive backup + Adobe Stock SFTP

Uses **rclone** for both (one tool, resumable, no passwords in scripts).

## One-time setup
```bash
brew install rclone

# Google Drive (opens a browser to log in)
rclone config create gdrive drive scope=drive.file

# Adobe Stock SFTP — get host/user/password from the contributor portal:
# Upload page → "Upload via FTP/SFTP" (credentials are portal-specific, not your Adobe login)
rclone config create adobestock sftp host sftp.contributor.adobestock.com \
  user <SFTP_USER> pass "$(rclone obscure '<SFTP_PASSWORD>')"
```
Verify the host shown in the portal; use what Adobe shows if it differs.

## Each batch
```bash
S=<path-to-this-skill>/scripts
bash $S/upload.sh batches/<batch> --dry-run   # show what would be sent
bash $S/upload.sh batches/<batch>             # Drive backup + Adobe SFTP
bash $S/upload.sh batches/<batch> --drive-only
```
Env overrides: `DRIVE_REMOTE` (default `gdrive`), `DRIVE_FOLDER` (default `microstock`),
`ADOBE_REMOTE` (default `adobestock`). Missing remote → that step is skipped with a message.

Drive gets the whole batch (plan, final JPEGs, CSV) so it doubles as a shareable download
folder. Adobe gets **only `final/*.jpg`**.

## Then, in the Adobe Stock contributor portal
1. Wait until the files appear under *Not submitted* (SFTP uploads can take a few minutes).
2. Click **Upload CSV** and choose `adobe_stock.csv` — titles, keywords, categories fill in.
3. Select all files of the batch → tick **"Created using generative AI tools"**; if people or
   property are visible, tick **"People and Property are fictional"**.
4. Spot-check a few titles/keywords, then **Submit**.
5. Rejections arrive by email/portal — note the reason in `upload.log` and feed it back into
   the next `stock-trend-research` run.
