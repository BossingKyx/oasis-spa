# Deploying Oasis to Vercel (public booking page)

The code is already prepared and pushed to **https://github.com/BossingKyx/oasis-spa**.
This makes a public, always-on copy at `https://<project>.vercel.app` (separate
cloud database from your local office install).

## One-time setup (in the browser, ~5 minutes)

1. **Import the repo**
   - Go to <https://vercel.com> → **Add New… → Project**.
   - Import **BossingKyx/oasis-spa** (your GitHub is already connected from 24K).
   - Framework preset: **Other**. Leave build settings as-is (`vercel.json` handles it).
   - Click **Deploy** once (the first build may fail until the database exists — that's expected; we fix it in step 2/3).

2. **Add a Postgres database**
   - In the project → **Storage → Create Database → Postgres** (Neon).
   - **Connect** it to the `oasis-spa` project. This auto-adds `DATABASE_URL` /
     `POSTGRES_URL` environment variables.

3. **Set environment variables** (project → **Settings → Environment Variables**)
   - `DEBUG` = `False`
   - `SECRET_KEY` = *(any long random string)*
   - (Host/CSRF are handled automatically via Vercel's `VERCEL_URL`.)

4. **Redeploy** (Deployments → ⋯ → Redeploy).
   - The build runs `build_files.sh`: installs deps, `collectstatic`,
     `migrate`, and `seed_demo` (creates the 2 branches, services, an owner,
     and therapists in the cloud database).

## After deploy
- Booking page: `https://<project>.vercel.app/book/`
- Admin login: `https://<project>.vercel.app/login/` → `owner` / `oasis123`
  — **change this password immediately** (Admin → Users).
- Update the QR/poster to point at the new public URL.

## Notes
- This cloud copy has its **own database**, separate from the local office
  install. Online bookings appear here, not in the on-PC system.
- Uploaded files (payment screenshots, receipts) do **not** persist on Vercel's
  temporary disk — keep those on the local install, or add S3/Supabase storage
  later. The public booking flow uploads nothing, so it is unaffected.
