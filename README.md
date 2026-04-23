# Corner29

Static SvelteKit marketing site for a G+4 office lease on Kondapur Main Road.

## Dev

```sh
npm install
npm run dev
```

Then:
- `/` — design picker
- `/design/commercial`
- `/design/architectural`
- `/design/boutique`
- `/design/editorial`

## Build

```sh
npm run build   # static output in build/
npm run preview
```

## Deploy (Fly.io)

```sh
fly launch --copy-config --no-deploy   # first time only, to create the app
fly deploy
```

## TODO
- Wire contact form to a real backend (Formspree, Web3Forms, or serverless). Currently simulates success client-side.
- Add visitor analytics (slot reserved in `src/app.html` head).
- Pick a winning design variant; remove the other three `src/routes/design/*` folders.
