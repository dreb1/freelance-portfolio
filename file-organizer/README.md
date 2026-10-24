# File Organizer

Turns a cluttered folder (Downloads, a shared drive, a client upload dump) into tidy subfolders in one command, and can undo it.

```
python organize.py ~/Downloads             # sort by type
python organize.py ~/Downloads --by date   # sort into 2026-09, 2026-10, ...
python organize.py ~/Downloads --dry-run   # preview only
python organize.py ~/Downloads --undo      # put everything back
```

## Example

```
$ python make_demo_folder.py
Created 17 files in demo_downloads

$ python organize.py demo_downloads
IMG_2041.jpg  ->  Images/IMG_2041.jpg
contract_signed.pdf  ->  Documents/contract_signed.pdf
q3_sales.xlsx  ->  Spreadsheets/q3_sales.xlsx
...

Moved 17 files:
  Archives       1
  Audio          1
  Code           1
  Documents      4
  Images         4
  Installers     1
  Other          1
  Presentations  1
  Spreadsheets   2
  Video          1
```

## Safety

- **Never overwrites.** If `report.pdf` already exists, the new one becomes `report (1).pdf`.
- **Dry run** shows every move before anything changes.
- **Undo** reads the log written on each run and restores the original layout.
- Standard library only, Python 3.9+. Nothing to install.

## Easy to customize

Categories are a plain dictionary at the top of `organize.py`, so it's quick to add rules such as "client invoices go to /Billing" or "RAW photos go to /Shoots/2026".
