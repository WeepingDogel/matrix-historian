/**
 * Timezone formatting utility
 * Converts UTC timestamps to the user's selected timezone
 */

import { writable, derived } from 'svelte/store';

function detectTimezone() {
	if (typeof window === 'undefined') return 'local';
	try {
		const saved = localStorage.getItem('mh-timezone');
		if (saved) return saved;
	} catch {}
	return 'local';
}

/** 'local' = browser timezone, 'UTC' = force UTC */
export const timezone = writable(detectTimezone());

export function setTimezone(tz) {
	timezone.set(tz);
	try { localStorage.setItem('mh-timezone', tz); } catch {}
}

/**
 * Normalize bare ISO timestamps from the API by appending 'Z' if missing.
 * The backend stores and returns UTC timestamps but without the 'Z' suffix
 * (e.g. "2026-03-14T13:44:48.472716"). Without 'Z', JS Date() treats them
 * as local time, causing incorrect timezone conversions.
 */
function normalizeUtcTimestamp(timestamp) {
	const s = String(timestamp);
	if (/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(s) && !/[Zz]|[+-]\d{2}/.test(s)) {
		return s + 'Z';
	}
	return s;
}

/**
 * Derived store: $formatTime(timestamp) returns localized date/time string
 */
export const formatTime = derived(timezone, ($tz) => {
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
		// Use browser locale for date format
		return d.toLocaleString(undefined, options);
	};
});

/** Export for use in analytics chart labels */
export { normalizeUtcTimestamp };
