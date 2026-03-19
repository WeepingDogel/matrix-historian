<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);

	function buildParams(overrides = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchInput;
		const page = overrides.page ?? currentPage;
		if (q) params.set('q', q);
		if (page > 1) params.set('page', String(page));
		return params.toString();
	}

	function doSearch(e) {
		e.preventDefault();
		goto(`/rooms?${buildParams({ page: 1 })}`);
	}
</script>

<svelte:head>
	<title>{$t('rooms.title')} – {$t('app.title')}</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">{$t('rooms.title')}</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
{/if}

<!-- Search -->
<form onsubmit={doSearch} class="flex gap-2 mb-6">
	<input
		type="text"
		placeholder={$t('rooms.filterPlaceholder')}
		class="input input-bordered flex-1 max-w-md"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">{$t('common.search')}</button>
	{#if data.query}
		<a href="/rooms" class="btn btn-ghost">{$t('common.clear')}</a>
	{/if}
</form>

<div class="flex justify-between items-center mb-4">
	<p class="text-sm opacity-60">
		{$t('rooms.roomCount', { count: data.total })}
		{#if data.query}{$t('messages.matching', { query: data.query })}{/if}
	</p>
	<p class="text-sm opacity-60">
		{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}
	</p>
</div>

{#if data.rooms.length === 0}
	<p class="opacity-60">{$t('rooms.noRooms')}</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>{$t('rooms.name')}</th>
					<th>{$t('rooms.roomId')}</th>
					<th class="text-right">{$t('rooms.messagesCol')}</th>
				</tr>
			</thead>
			<tbody>
				{#each data.rooms as room}
					<tr class="hover">
						<td>
							<a href="/rooms/{encodeURIComponent(room.room_id)}" class="link link-hover font-medium">
								{room.name || $t('common.unnamed')}
							</a>
						</td>
						<td class="font-mono text-xs opacity-70">{room.room_id}</td>
						<td class="text-right">
							{#if data.activityMap[room.room_id] !== undefined}
								<span class="badge badge-sm">{data.activityMap[room.room_id].toLocaleString()}</span>
							{:else}
								<span class="opacity-40">—</span>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Pagination -->
	<div class="flex items-center gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a
				href="/rooms?{buildParams({ page: currentPage - 1 })}"
				class="btn btn-outline btn-sm"
			>
				{$t('common.previous')}
			</a>
		{/if}
		<span class="text-sm opacity-60">{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}</span>
		{#if data.hasMore}
			<a
				href="/rooms?{buildParams({ page: currentPage + 1 })}"
				class="btn btn-outline btn-sm"
			>
				{$t('common.next')}
			</a>
		{/if}
	</div>
{/if}
