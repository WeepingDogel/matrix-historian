/**
 * Lightweight i18n store for Matrix Historian
 * Supports: en, zh-CN
 * Usage: import { t, locale, setLocale } from '$lib/i18n';
 *        {$t('dashboard.title')}
 */

import { writable, derived } from 'svelte/store';

import en from './locales/en.json';
import zhCN from './locales/zh-CN.json';

const translations = { en, 'zh-CN': zhCN };
export const supportedLocales = [
	{ code: 'en', label: 'English' },
	{ code: 'zh-CN', label: '简体中文' }
];

function detectLocale() {
	if (typeof window === 'undefined') return 'en';
	try {
		const saved = localStorage.getItem('mh-locale');
		if (saved && translations[saved]) return saved;
	} catch {}
	const nav = navigator.language || 'en';
	if (nav.startsWith('zh')) return 'zh-CN';
	return 'en';
}

export const locale = writable(detectLocale());

export function setLocale(code) {
	if (translations[code]) {
		locale.set(code);
		try { localStorage.setItem('mh-locale', code); } catch {}
	}
}

/**
 * Resolve a dotted key path like 'dashboard.title' from a translations object
 */
function resolve(obj, path) {
	return path.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : null), obj);
}

/**
 * Derived store: $t('key') returns translated string, falls back to English, then the key itself
 */
export const t = derived(locale, ($locale) => {
	return (key, params) => {
		let str = resolve(translations[$locale], key)
			?? resolve(translations['en'], key)
			?? key;
		if (params) {
			Object.entries(params).forEach(([k, v]) => {
				str = str.replaceAll(`{${k}}`, String(v));
			});
		}
		return str;
	};
});
