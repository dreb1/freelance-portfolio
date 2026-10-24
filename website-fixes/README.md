# Website Bug Fixes: Before & After

A small business landing page with six common real-world bugs, and the fixed version. Open `before/index.html` and `after/index.html` side by side, or shrink the browser to phone width, to see the difference.

| # | Problem the owner noticed | Cause | Fix |
|---|---|---|---|
| 1 | Page scrolls sideways on phones | Hero section set to `width: 1200px` | Fluid width, with text capped at a readable 720px |
| 2 | Site looks tiny and zoomed-out on phones | Missing viewport meta tag | Added `<meta name="viewport" content="width=device-width, initial-scale=1">` |
| 3 | "Menu" button does nothing on mobile | Script ran in `<head>` before the button existed (`Cannot read properties of null`) | Moved the script to the end of `<body>`; added `aria-expanded` for screen readers |
| 4 | Service photos spill out of their boxes | Images had no size limit | `max-width: 100%; height: auto` and `min-width: 0` on the cards |
| 5 | Tagline is hard to read | Light grey text (`#b5c4bd`) on light green: contrast 1.6:1, far below the 4.5:1 minimum | Darkened to `#2f4f43`: contrast 8.1:1, passes WCAG AAA |
| 6 | Quote form "loses" messages | Button reloaded the page; empty forms went through | Labeled fields, email validation, no reload, clear success message |

Each fix is marked with a `FIX n` comment in `after/index.html`, matching the `BUG n` comments in `before/index.html`.

## How I work on client sites

1. Reproduce the problem on desktop and phone sizes.
2. Find the cause in the browser dev tools (console errors, layout inspector).
3. Make the smallest change that fixes it, without redesigning what already works.
4. Retest on phone and desktop, then send a short note like the table above explaining what changed.
