<script>
	import { locale, setLocale, supportedLocales, t } from '$lib/i18n';
	import { timezone, setTimezone } from '$lib/timezone';
	import { theme, setTheme, supportedThemes } from '$lib/theme';
</script>

<div class="flex flex-col gap-2 px-2">
	<!-- Language selector -->
	<div class="flex items-center gap-2">
		<span class="text-xs opacity-60">🌐</span>
		<select
			class="select select-bordered select-xs flex-1"
			value={$locale}
			onchange={(e) => setLocale(e.target.value)}
		>
			{#each supportedLocales as loc}
				<option value={loc.code}>{loc.label}</option>
			{/each}
		</select>
	</div>
	<!-- Timezone selector -->
	<div class="flex items-center gap-2">
		<span class="text-xs opacity-60">🕐</span>
		<select
			class="select select-bordered select-xs flex-1"
			value={$timezone}
			onchange={(e) => setTimezone(e.target.value)}
		>
			<option value="local">{$t('timezone.local')}</option>
			<option value="UTC">UTC</option>
		</select>
	</div>
	<!-- Theme selector -->
	<div class="flex items-center gap-2">
		<span class="text-xs opacity-60">🎨</span>
		<select
			class="select select-bordered select-xs flex-1"
			value={$theme}
			onchange={(e) => setTheme(e.target.value)}
		>
			{#each supportedThemes as th}
				<option value={th.code}>{th.label}</option>
			{/each}
		</select>
	</div>
</div>
