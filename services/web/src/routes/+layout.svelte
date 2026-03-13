<script>
	import '../app.css';
	import { page } from '$app/state';
	import { t } from '$lib/i18n';
	import LocalePicker from '$lib/LocalePicker.svelte';

	let { children } = $props();

	const navItems = [
		{ href: '/', labelKey: 'nav.dashboard', icon: '📊' },
		{ href: '/messages', labelKey: 'nav.messages', icon: '💬' },
		{ href: '/rooms', labelKey: 'nav.rooms', icon: '🏠' },
		{ href: '/users', labelKey: 'nav.users', icon: '👥' },
		{ href: '/media', labelKey: 'nav.media', icon: '🖼️' },
		{ href: '/analytics', labelKey: 'nav.analytics', icon: '📈' }
	];

	function isActive(href) {
		const path = page.url?.pathname ?? '/';
		if (href === '/') return path === '/';
		return path === href || path.startsWith(href + '/');
	}
</script>

<div class="drawer lg:drawer-open">
	<input id="sidebar-drawer" type="checkbox" class="drawer-toggle" />

	<!-- Main content -->
	<div class="drawer-content flex flex-col min-h-screen">
		<!-- Navbar for mobile -->
		<div class="navbar bg-base-200 lg:hidden">
			<div class="flex-none">
				<label for="sidebar-drawer" class="btn btn-square btn-ghost drawer-button">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
						class="inline-block w-6 h-6 stroke-current">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
							d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</label>
			</div>
			<div class="flex-1">
				<span class="text-xl font-bold">{$t('app.title')}</span>
			</div>
		</div>

		<!-- Page content -->
		<main class="flex-1 p-4 md:p-6">
			{@render children()}
		</main>

		<!-- Footer -->
		<footer class="footer footer-center p-4 text-base-content/50 text-xs">
			<p>{$t('app.footer')}</p>
		</footer>
	</div>

	<!-- Sidebar -->
	<div class="drawer-side z-40">
		<label for="sidebar-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
		<aside class="bg-base-200 min-h-full w-64 p-4 flex flex-col">
			<div class="mb-8 px-2">
				<a href="/" class="block">
					<h1 class="text-xl font-bold">📜 {$t('app.title')}</h1>
					<p class="text-xs opacity-60 mt-1">{$t('app.subtitle')}</p>
				</a>
			</div>
			<ul class="menu gap-1">
				{#each navItems as item}
					<li>
						<a href={item.href} class="text-base" class:active={isActive(item.href)}>
							<span>{item.icon}</span>
							{$t(item.labelKey)}
						</a>
					</li>
				{/each}
			</ul>

			<!-- Sidebar stats summary -->
			<div class="mt-auto pt-8 px-2">
				<div class="divider text-xs opacity-40">{$t('nav.quickLinks')}</div>
				<ul class="menu menu-xs gap-0.5 opacity-70">
					<li><a href="/analytics">📊 {$t('nav.viewAnalytics')}</a></li>
					<li><a href="/media">🖼️ {$t('nav.mediaGallery')}</a></li>
				</ul>

				<!-- Locale & timezone picker -->
				<div class="divider text-xs opacity-40">🌐</div>
				<LocalePicker />
			</div>
		</aside>
	</div>
</div>
