# microstock-skills — index for agents

Skills live in `skills/<name>/SKILL.md`. Read the matching one fully before acting.

| Skill | Load when |
| ----- | --------- |
| `skills/stock-pipeline` | user wants to sell AI images on Adobe Stock / start a microstock batch / asks what's next |
| `skills/stock-trend-research` | find trending or in-demand stock topics; write plan.csv |
| `skills/stock-image-batch` | generate many images from plan.csv (needs image generation → Codex/OpenAI); upscale to stock specs |
| `skills/stock-metadata-csv` | titles, keywords, categories, Adobe Stock CSV |
| `skills/stock-upload` | Google Drive backup, Adobe Stock SFTP upload, portal CSV import |

Rules:
- Batches live in `batches/<YYYY-MM-DD>-<slug>/` (git-ignored). Never commit `.env` or API keys.
- Image generation costs money: always test `--limit 3` and get the user's go before a full run.
- Never use brands, real people, characters, or artist names in prompts or metadata.
- If you cannot generate images (e.g. Claude), finish your step and tell the user to run the next step in Codex.
