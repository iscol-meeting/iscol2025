ISCOL 2025 — Static Site

This is a simple static website for ISCOL 2025 (Israel Seminar on Computational Linguistics), modeled after the ISCOL 2024 site but with all content marked TBD. The event is planned to take place at Bar-Ilan University.

- Live reference (previous year): https://sites.google.com/ds.haifa.ac.il/iscol2024/home?authuser=0

Files
- `index.html` — Main page with sections: Home, Call for Papers, Program, Posters, FAQ
- `styles.css` — Minimal responsive styling and navigation

Local Development
No build step is required. Open the `index.html` file in any modern browser.

```bash
open index.html
```

For a quick local server (optional):

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

Deployment
Any static hosting solution works (e.g., GitHub Pages, Netlify, Vercel, S3/CloudFront). Upload the two files `index.html` and `styles.css`.

Content Status
All content is placeholders (TBD). Replace as details become available:
- Location details, room, campus access
- Important dates and submission site
- Program schedule and invited talks
- Poster session assignments and guidelines
- Contact information

License
MIT


