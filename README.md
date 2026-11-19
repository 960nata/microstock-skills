# microstock-skills

Skill untuk AI agent (Codex, Claude Code, Antigravity, Gemini CLI) yang mengurus
**jualan gambar AI di Adobe Stock** dari awal sampai akhir: riset apa yang lagi dicari
orang, generate 100 gambar sekaligus, bikin title + keyword SEO dalam bentuk CSV, backup ke Google
Drive, lalu upload.

> Agent skills for selling AI images on Adobe Stock: trend research → batch generation →
> SEO metadata CSV → Drive backup → SFTP upload.

## Alurnya

```
 Claude                     Codex                        Claude / Codex           siapa saja
 ──────                     ─────                        ──────────────           ──────────
 stock-trend-research  ─►   stock-image-batch       ─►   stock-metadata-csv  ─►   stock-upload
 riset tren + 100 prompt    generate + JPEG ≥4MP         title, keyword, CSV      Drive + Adobe SFTP
 plan.csv                   raw/ → final/                adobe_stock.csv          upload.log
```

Claude tidak bisa bikin gambar, jadi tahap generate dikerjakan **Codex** lewat OpenAI
Images API. Tahap lain bisa dikerjakan agent mana saja. Satu batch disimpan di satu
folder (`batches/<tanggal>-<tema>/`), jadi agent mana pun bisa melanjutkan dari tahap
terakhir.

| Skill | Isinya |
| ----- | ------ |
| [`stock-pipeline`](skills/stock-pipeline/SKILL.md) | Peta alur, struktur folder, aturan supaya gambar diterima |
| [`stock-trend-research`](skills/stock-trend-research/SKILL.md) | Cari tema yang permintaannya tinggi tapi pesaingnya sedikit, kalender musiman, lalu tulis 100 prompt variatif ke `plan.csv` |
| [`stock-image-batch`](skills/stock-image-batch/SKILL.md) | `generate_images.py` (paralel, bisa dilanjutkan kalau putus, retry otomatis) + `prepare_images.py` (upscale ke ≥4MP, JPEG) |
| [`stock-metadata-csv`](skills/stock-metadata-csv/SKILL.md) | Title + 30–49 keyword urut prioritas + kategori → `build_csv.py` (validasi + cek kata merek dagang) |
| [`stock-upload`](skills/stock-upload/SKILL.md) | `upload.sh` pakai rclone: backup ke Google Drive + SFTP ke Adobe, lalu panduan import CSV di portal |

## Pasang

```bash
git clone <repo-ini> && cd microstock-skills
./install.sh codex claude        # atau: ./install.sh all
pip3 install pillow              # untuk upscale
brew install rclone              # untuk upload (Drive + Adobe SFTP)
```

## Pakai (contoh percakapan)

1. **Claude:** *"Pakai stock-trend-research, cariin tema Ramadan 2027 yang laku di Adobe Stock, bikin batch 100 gambar."*
   Hasilnya `batches/2026-11-20-ramadan/plan.csv`.
2. **Codex:** *"Pakai stock-image-batch di batches/2026-11-20-ramadan, tes 3 dulu."* Kalau hasilnya oke: *"lanjut semua."*
   `OPENAI_API_KEY` wajib diset dulu. **Ini berbayar**, jadi script selalu menawarkan tes 3 gambar dulu.
3. **Claude/Codex:** *"Pakai stock-metadata-csv untuk batch itu."* Hasilnya `adobe_stock.csv` yang sudah divalidasi.
4. *"Upload batch itu."* File-nya masuk ke Drive dan Adobe, lalu di portal: **Upload CSV** → centang **"Created using generative AI tools"** → **Submit**.

Coba script tanpa API dengan contoh yang sudah ada:
```bash
python3 skills/stock-image-batch/scripts/generate_images.py examples/demo-batch --dry-run
python3 skills/stock-metadata-csv/scripts/build_csv.py examples/demo-batch   # sengaja ada error untuk contoh
```

## Aturan penting Adobe Stock

- Wajib centang **"Created using generative AI tools"** untuk semua gambar AI.
- Jangan ada merek, logo, karakter, selebriti, orang asli, atau nama seniman, baik di prompt, title, maupun keyword.
- Hindari gambar yang mirip-mirip. Lebih baik 100 gambar dari 20 konsep yang beda jelas daripada 100 gambar yang hampir sama.
- Buang gambar yang cacat (tangan aneh, tulisan rusak). Tingkat penolakan yang tinggi bisa bikin kuota upload kamu dibatasi.
- Aturan Adobe bisa berubah, jadi cek *Generative AI content guidelines* di Contributor help center sebelum batch besar.

## License

MIT
