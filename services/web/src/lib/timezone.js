/**
 * Timezone formatting utility
 * Converts UTC timestamps to the user's selected timezone
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

function detectTimezone() {
	if (!browser) return 'UTC';  // SSR always renders UTC
	try {
		const saved = localStorage.getItem('mh-timezone');
		if (saved) return saved;
	} catch {}
	return 'local';
}

/** 'local' = browser timezone, 'UTC' = force UTC */
export const timezone = writable(detectTimezone());

/**
 * Hydration fix: Svelte 5 doesn't re-validate text nodes during hydration,
 * so SSR-rendered UTC timestamps stay in the DOM even when the client would
 * produce different values. This tick store forces formatTime to recompute
 * after hydration by changing a dependency from 0 → 1.
 */
const _hydrated = writable(0);
if (browser) {
	setTimeout(() => _hydrated.set(1), 0);
}

export function setTimezone(tz) {
	timezone.set(tz);
	try { localStorage.setItem('mh-timezone', tz); } catch {}
}

/**
 * Normalize bare ISO timestamps from the API by appending 'Z' if missing.
 */
function normalizeUtcTimestamp(timestamp) {
	const s = String(timestamp);
	if (/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(s) && !/[Zz]|[+-]\d{2}/.test(s)) {
		return s + 'Z';
	}
	return s;
}

/**
 * Derived store: $formatTime(timestamp) returns localized date/time string.
 * Depends on both timezone and _hydrated so it recomputes after hydration.
 */
export const formatTime = derived([timezone, _hydrated], ([$tz]) => {
	return (timestamp) => {
		if (!timestamp) return '';
		const normalized = normalizeUtcTimestamp(timestamp);
		const d = new Date(normalized);
		if (isNaN(d.getTime())) return String(timestamp);
		const options = {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		};
		if ($tz === 'UTC') {
			options.timeZone = 'UTC';
		}
		return d.toLocaleString(undefined, options);
	};
});

/** Export for use in analytics chart labels */
export { normalizeUtcTimestamp };
