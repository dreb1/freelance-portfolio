"""Create a cluttered demo folder to try organize.py on."""

from pathlib import Path

NAMES = [
    "IMG_2041.jpg", "IMG_2042.jpg", "screenshot 2026-09-14.png", "logo-final-v3.png",
    "invoice_0921.pdf", "contract_signed.pdf", "notes.txt", "resume.docx",
    "q3_sales.xlsx", "customers.csv", "pitch_deck.pptx", "podcast_ep12.mp3",
    "product_demo.mp4", "backup_photos.zip", "setup.exe", "script.py", "random.xyz",
]

demo = Path("demo_downloads")
demo.mkdir(exist_ok=True)
for name in NAMES:
    (demo / name).write_text("demo file\n", encoding="utf-8")
print(f"Created {len(NAMES)} files in {demo.resolve()}")
