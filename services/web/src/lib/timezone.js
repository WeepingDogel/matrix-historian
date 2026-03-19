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
 * Derived store: $formatTime(timestamp) returns localized date/time string.
 * Depends on both timezone and _hydrated so it recomputes after hydration.
 *
 * Timestamps from the API are now timezone-aware (ISO 8601 with Z suffix)
 * thanks to the backend TIMESTAMPTZ migration. No client-side normalization needed.
 */
export const formatTime = derived([timezone, _hydrated], ([$tz]) => {
	return (timestamp) => {
		if (!timestamp) return '';
		const d = new Date(String(timestamp));
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
