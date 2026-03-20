<script>
	/**
	 * Reusable infinite scroll component.
	 * Place at the bottom of a list. Fires `onLoadMore` when the sentinel enters viewport.
	 */
	import { t } from '$lib/i18n';

	let { loading = false, hasMore = true, onLoadMore = () => {} } = $props();
	let sentinel;

	$effect(() => {
		if (!sentinel) return;
		const observer = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting && hasMore && !loading) {
					onLoadMore();
				}
			},
			{ rootMargin: '200px' }
		);
		observer.observe(sentinel);
		return () => observer.disconnect();
	});
</script>

<div bind:this={sentinel} class="h-1"></div>
{#if loading}
	<div class="flex justify-center py-4">
		<span class="loading loading-spinner loading-md"></span>
	</div>
{/if}
{#if !hasMore && !loading}
	<p class="text-center text-sm opacity-50 py-4">{$t('common.allLoaded')}</p>
{/if}
