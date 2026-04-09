import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export const supportedThemes = [
	{ code: 'dark', label: 'Dark' },
	{ code: 'light', label: 'Light' },
	{ code: 'cupcake', label: 'Cupcake' },
	{ code: 'dracula', label: 'Dracula' },
	{ code: 'nord', label: 'Nord' },
	{ code: 'sunset', label: 'Sunset' }
];

function detectTheme() {
	if (!browser) return 'dark';
	try {
		const saved = localStorage.getItem('mh-theme');
		if (saved && supportedThemes.some(t => t.code === saved)) return saved;
	} catch {}
	return 'dark';
}

export const theme = writable(detectTheme());

export function setTheme(code) {
	if (supportedThemes.some(t => t.code === code)) {
		theme.set(code);
		if (browser) {
			try { localStorage.setItem('mh-theme', code); } catch {}
			document.documentElement.setAttribute('data-theme', code);
		}
	}
}

// Apply saved theme on load
if (browser) {
	document.documentElement.setAttribute('data-theme', detectTheme());
}
