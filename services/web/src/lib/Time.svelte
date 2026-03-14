<script>
	/**
	 * Client-only timestamp renderer.
	 * Bypasses SSR hydration issues by only formatting timestamps after mount.
	 * SSR renders nothing; client renders correctly localized time.
	 */
	import { onMount } from 'svelte';
	import { formatTime } from '$lib/timezone';

	let { timestamp } = $props();
	let display = $state('');

	onMount(() => {
		const unsub = formatTime.subscribe(fn => {
			display = fn(timestamp);
		});
		return unsub;
	});
</script>{display}
