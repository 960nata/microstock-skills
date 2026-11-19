# microstock-skills

<p>
  <img alt="skills" src="https://img.shields.io/badge/skills-5-34d399">
  <img alt="agents" src="https://img.shields.io/badge/works%20with-Codex%20%7C%20Claude%20Code%20%7C%20Antigravity%20%7C%20Gemini-a3e635">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-lightgrey">
</p>

**Agent skills that run your Adobe Stock side hustle from start to finish.**
Find what buyers are searching for, generate 100 images in one go, write SEO titles and
keywords, build the contributor CSV, back up to Google Drive, and upload. All of it
happens by talking to your AI agent.

## How it works

```
 Claude                     Codex                        Claude / Codex           any agent
 ──────                     ─────                        ──────────────           ─────────
 stock-trend-research  ─►   stock-image-batch       ─►   stock-metadata-csv  ─►   stock-upload
 trends + 100 prompts       generate + JPEG ≥ 4 MP       titles, keywords, CSV    Drive + Adobe SFTP
 plan.csv                   raw/ → final/                adobe_stock.csv          upload.log
```

Claude can't generate images, so **Codex** handles generation through the OpenAI Images
API, and any agent can handle the other steps. Each batch lives in its own folder
(`batches/<date>-<theme>/`). Every step reads the previous step's files, so you can
switch agents at any point.

| Skill | What it does |
| ----- | ------------ |
| [`stock-pipeline`](skills/stock-pipeline/SKILL.md) | Workflow map, folder layout, and the rules that get images accepted |
| [`stock-trend-research`](skills/stock-trend-research/SKILL.md) | Finds themes with high demand and few competing images, plans around the seasonal calendar, and writes 100 varied, IP-free prompts to `plan.csv` |
| [`stock-image-batch`](skills/stock-image-batch/SKILL.md) | `generate_images.py` generates in parallel, retries failures, and can resume where it stopped. `prepare_images.py` upscales to ≥ 4 MP JPEG |
| [`stock-metadata-csv`](skills/stock-metadata-csv/SKILL.md) | Writes a title, 30–49 keywords ranked by importance, and a category for each image. `build_csv.py` validates them and flags trademark words |
| [`stock-upload`](skills/stock-upload/SKILL.md) | `upload.sh` uses rclone to back up to Google Drive and upload to Adobe Stock over SFTP, then guides the CSV import in the portal |

## Setup (once)

```bash
git clone https://github.com/960nata/microstock-skills.git && cd microstock-skills
./install.sh codex claude                # or: ./install.sh all
pip3 install pillow                      # image upscaling
brew install rclone                      # uploads (Google Drive + Adobe SFTP)
export OPENAI_API_KEY="sk-..."           # image generation (paid API key)

rclone config create gdrive drive scope=drive.file
rclone config create adobestock sftp host sftp.contributor.adobestock.com \
  user <SFTP_USER> pass "$(rclone obscure '<SFTP_PASSWORD>')"
```
Get your SFTP credentials from the Adobe Stock contributor portal (**Upload → Upload via FTP/SFTP**).

## Usage

Open your agent inside this folder and just talk to it:

1. **Claude:** *"Use stock-trend-research to find what will sell on Adobe Stock in the next two months and plan a 100-image batch."*
2. **Codex:** *"Use stock-image-batch on batches/2026-11-20-ramadan, test 3 images first."* If they look good: *"Run the rest."* Then: *"Prepare them for Adobe Stock."*
3. **Claude or Codex:** *"Use stock-metadata-csv on that batch."*
4. **Any agent:** *"Upload that batch."*
5. **Adobe Stock portal:** **Upload CSV** → tick **"Created using generative AI tools"** → **Submit**.

Try the scripts without spending anything:
```bash
python3 skills/stock-image-batch/scripts/generate_images.py examples/demo-batch --dry-run
python3 skills/stock-metadata-csv/scripts/build_csv.py examples/demo-batch   # includes a deliberate error
```

## Tips

- **Image generation costs money.** The workflow always tests 3 images first, and `--price-per-image` prints an estimated total.
- **If a run stops halfway,** run the same command again. Finished images are skipped.
- **Start small.** Submit 20–30 images, check your acceptance rate, then scale up.
- **Feed rejection reasons back** into the next research run so the same mistakes don't repeat.

## Adobe Stock rules that matter

- Tick **"Created using generative AI tools"** on every AI image.
- Leave out brands, logos, characters, celebrities, real people, and artist names, both in prompts and in metadata.
- Avoid near-duplicates. 100 images should come from 15–25 clearly different concepts.
- Remove flawed images (bad hands, garbled text). A high rejection rate can lower your upload limits.
- Rules change. Before a big batch, check the current *Generative AI content* guidelines in the Contributor help center.

## License

[MIT](LICENSE) © Dicky Hadinata. Not affiliated with Adobe or OpenAI.
