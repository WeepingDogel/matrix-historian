<script>
	/**
	 * Client-only timestamp renderer.
	 * Bypasses SSR hydration issues by only formatting timestamps after mount.
	 * SSR renders nothing; client renders correctly localized time.
	 *
	 * Uses $effect to re-render when timestamp prop or formatTime store changes.
	 */
	import { onMount } from 'svelte';
	import { formatTime } from '$lib/timezone';

	let { timestamp } = $props();
	let mounted = $state(false);
	let display = $state('');

	onMount(() => {
		mounted = true;
	});

	$effect(() => {
		if (mounted) {
			const unsub = formatTime.subscribe(fn => {
				display = fn(timestamp);
			});
			return unsub;
		}
	});
</script>{display}
