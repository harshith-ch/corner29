// In-memory cache + background prefetch for floor-plan SVGs.
//
// Floor-plan SVGs are hundreds of KB each even after optimization. Fetching on
// demand makes every floor switch wait on a full network round-trip. Instead
// we prefetch all of them once the current tab is idle, share a single
// in-flight promise per URL, and hand the cached text back to the viewer on
// subsequent reads.

// Unbounded on purpose: the caller set is the 8 floor-plan URLs baked into
// the listing content. Do not hand this to user-supplied URLs — it'll grow
// without eviction.
const cache = new Map<string, Promise<string>>();

export function loadSvgText(url: string): Promise<string> {
  const existing = cache.get(url);
  if (existing) return existing;
  const p = fetch(url)
    .then((r) => {
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.text();
    })
    .catch((e) => {
      // Don't keep a rejected promise cached — let the next caller retry.
      cache.delete(url);
      throw e;
    });
  cache.set(url, p);
  return p;
}

export function prefetchSvgs(urls: string[]) {
  if (typeof window === 'undefined') return;
  const run = () => {
    for (const u of urls) {
      if (!cache.has(u)) loadSvgText(u).catch(() => {});
    }
  };
  // requestIdleCallback isn't available in Safari; fall back to a small delay.
  const ric = (window as unknown as { requestIdleCallback?: (cb: () => void) => void })
    .requestIdleCallback;
  if (typeof ric === 'function') ric(run);
  else setTimeout(run, 300);
}
