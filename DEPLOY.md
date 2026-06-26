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

2. **Create a Supabase database**
   - <https://supabase.com> → **New project** (free tier). Pick a region close
     to PH (e.g. Singapore) and save the database password.
   - Project → **Settings → Database → Connection string → "Session pooler"**.
     Copy the URI. It looks like:
     `postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres`
   - ⚠ Use the **pooler** host (`...pooler.supabase.com`), not the direct
     `db.<ref>.supabase.co` host — the direct one is IPv6-only and Vercel can't
     reach it.

3. **Set environment variables** (project → **Settings → Environment Variables**)
   - `DATABASE_URL` = *(the Supabase Session pooler URI from step 2)*
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
