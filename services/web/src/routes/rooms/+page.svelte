<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import InfiniteScroll from '$lib/InfiniteScroll.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import { getRooms, getRoomsCount, getRoomActivity, searchRooms, getSearchRoomsCount } from '$lib/api.js';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');
	let pageLoading = $state(true);

	// Accumulated items for infinite scroll
	let allRooms = $state([]);
	let currentSkip = $state(0);
	let hasMore = $state(false);
	let loading = $state(false);

	async function fetchRooms() {
		pageLoading = true;
		try {
			const q = data.query;
			const limit = data.limit;
			const [rooms, countResult, activity] = await Promise.all([
				q ? searchRooms(q, { skip: 0, limit }) : getRooms({ skip: 0, limit }),
				q ? getSearchRoomsCount(q) : getRoomsCount(),
				getRoomActivity(200).catch(() => ({ rooms: [] }))
			]);
			const total = countResult.total ?? 0;
			const activityMap = {};
			for (const r of activity.rooms ?? []) {
				const id = r.room_id || r.room;
				if (id) activityMap[id] = r.message_count ?? 0;
			}
			data = { ...data, rooms, activityMap, total, hasMore: total > limit, nextSkip: limit, _loading: false };
			allRooms = [...rooms];
			currentSkip = rooms.length;
			hasMore = total > limit;
		} catch (e) {
			console.error('Rooms fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	$effect(() => {
		void data.query;
		fetchRooms();
	});

	function doSearch(e) {
		e.preventDefault();
		const params = new URLSearchParams();
		if (searchInput.trim()) params.set('q', searchInput.trim());
		goto(`/rooms?${params.toString()}`);
	}

	async function loadMore() {
		if (loading || !hasMore) return;
		loading = true;
		try {
			const apiParams = new URLSearchParams();
			apiParams.set('skip', String(currentSkip));
			apiParams.set('limit', String(data.limit));

			const endpoint = data.query
				? `/api/v1/rooms/search?query=${encodeURIComponent(data.query)}&${apiParams.toString()}`
				: `/api/v1/rooms?${apiParams.toString()}`;

			const res = await fetch(endpoint);
			if (!res.ok) throw new Error(`API ${res.status}`);
			const newRooms = await res.json();

			allRooms = [...allRooms, ...newRooms];
			currentSkip += newRooms.length;
			hasMore = newRooms.length >= data.limit;
		} catch (e) {
			console.error('Load more error:', e);
			hasMore = false;
		} finally {
			loading = false;
		}
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

{#if pageLoading}
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
				<Skeleton variant="table-row" count={5} />
			</tbody>
		</table>
	</div>
{:else}
	<div class="flex justify-between items-center mb-4">
		<p class="text-sm opacity-60">
			{$t('rooms.roomCount', { count: data.total })}
			{#if data.query}{$t('messages.matching', { query: data.query })}{/if}
		</p>
		<p class="text-sm opacity-60">
			{allRooms.length} / {data.total}
		</p>
	</div>

	{#if allRooms.length === 0 && !loading}
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
					{#each allRooms as room (room.room_id)}
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

		<InfiniteScroll {loading} {hasMore} onLoadMore={loadMore} />
	{/if}
{/if}
