<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import InfiniteScroll from '$lib/InfiniteScroll.svelte';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');
	let selectedRoom = $state(data.room_id ?? '');
	let selectedUser = $state(data.user_id ?? '');
	let startDate = $state(data.start_date ?? '');
	let endDate = $state(data.end_date ?? '');

	// Accumulated messages for infinite scroll
	let allMessages = $state([...data.messages]);
	let currentSkip = $state(data.skip + data.messages.length);
	let hasMore = $state(data.hasMore);
	let loading = $state(false);

	// Reset accumulated messages when filters/data change via navigation
	$effect(() => {
		allMessages = [...data.messages];
		currentSkip = data.skip + data.messages.length;
		hasMore = data.hasMore;
		loading = false;
	});

	function buildFilterParams(overrides = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchInput;
		const room = overrides.room_id ?? selectedRoom;
		const user = overrides.user_id ?? selectedUser;
		const sd = overrides.start_date ?? startDate;
		const ed = overrides.end_date ?? endDate;
		if (q) params.set('q', q);
		if (room) params.set('room_id', room);
		if (user) params.set('user_id', user);
		if (sd) params.set('start_date', sd);
		if (ed) params.set('end_date', ed);
		return params.toString();
	}

	function doSearch(e) {
		e.preventDefault();
		goto(`/messages?${buildFilterParams()}`);
	}

	function onFilterChange() {
		goto(`/messages?${buildFilterParams()}`);
	}

	function clearFilters() {
		searchInput = '';
		selectedRoom = '';
		selectedUser = '';
		startDate = '';
		endDate = '';
		goto('/messages');
	}

	async function loadMore() {
		if (loading || !hasMore) return;
		loading = true;
		try {
			const params = new URLSearchParams();
			params.set('skip', String(currentSkip));
			params.set('limit', String(data.limit));
			if (data.query) params.set('q', data.query);
			if (data.room_id) params.set('room_id', data.room_id);
			if (data.user_id) params.set('user_id', data.user_id);
			if (data.start_date) params.set('start_date', data.start_date);
			if (data.end_date) params.set('end_date', data.end_date);

			// Build the correct API path
			const after = data.start_date ? `${data.start_date}T00:00:00Z` : '';
			const before = data.end_date ? `${data.end_date}T23:59:59Z` : '';

			const apiParams = new URLSearchParams();
			apiParams.set('skip', String(currentSkip));
			apiParams.set('limit', String(data.limit));
			if (data.query) apiParams.set('query', data.query);
			if (data.room_id) apiParams.set('room_id', data.room_id);
			if (data.user_id) apiParams.set('user_id', data.user_id);
			if (after) apiParams.set('after', after);
			if (before) apiParams.set('before', before);

			const endpoint = data.query ? '/api/v1/search' : '/api/v1/messages';
			const res = await fetch(`${endpoint}?${apiParams.toString()}`);
			if (!res.ok) throw new Error(`API ${res.status}`);
			const result = await res.json();

			const newMessages = result.messages ?? [];
			allMessages = [...allMessages, ...newMessages];
			currentSkip += newMessages.length;
			hasMore = result.has_more ?? false;
		} catch (e) {
			console.error('Load more error:', e);
			hasMore = false;
		} finally {
			loading = false;
		}
	}

	let hasFilters = $derived(data.query || data.room_id || data.user_id || data.start_date || data.end_date);
</script>

<svelte:head>
	<title>{$t('messages.title')} – {$t('app.title')}</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">{$t('messages.title')}</h2>

{#if data.error}
	<div class="alert alert-warning mb-4">
		<span>{$t('common.error', { error: data.error })}</span>
	</div>
{/if}

<!-- Search bar -->
<form onsubmit={doSearch} class="flex flex-wrap gap-2 mb-4">
	<input
		type="text"
		placeholder={$t('messages.searchPlaceholder')}
		class="input input-bordered flex-1 min-w-48"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">{$t('common.search')}</button>
	{#if hasFilters}
		<button type="button" class="btn btn-ghost" onclick={clearFilters}>{$t('common.clearAll')}</button>
	{/if}
</form>

<!-- Filters -->
<div class="flex flex-wrap gap-2 mb-6 items-center">
	<select class="select select-bordered select-sm" bind:value={selectedRoom} onchange={onFilterChange}>
		<option value="">{$t('messages.allRooms')}</option>
		{#each data.rooms as room}
			<option value={room.room_id}>{room.name || room.room_id}</option>
		{/each}
	</select>
	<select class="select select-bordered select-sm" bind:value={selectedUser} onchange={onFilterChange}>
		<option value="">{$t('messages.allUsers')}</option>
		{#each data.users as user}
			<option value={user.user_id}>{user.display_name || user.user_id}</option>
		{/each}
	</select>

	<!-- Date range -->
	<div class="flex items-center gap-1">
		<label class="text-xs opacity-60 whitespace-nowrap">{$t('messages.dateFrom')}</label>
		<input
			type="date"
			class="input input-bordered input-sm w-36"
			bind:value={startDate}
			onchange={onFilterChange}
		/>
	</div>
	<div class="flex items-center gap-1">
		<label class="text-xs opacity-60 whitespace-nowrap">{$t('messages.dateTo')}</label>
		<input
			type="date"
			class="input input-bordered input-sm w-36"
			bind:value={endDate}
			onchange={onFilterChange}
		/>
	</div>
</div>

<div class="flex justify-between items-center mb-4">
	<p class="text-sm opacity-60">
		{$t('messages.messageCount', { count: data.total.toLocaleString() })}
		{#if data.query}{$t('messages.matching', { query: data.query })}{/if}
		{#if data.room_id}{$t('messages.inRoom')}{/if}
		{#if data.user_id}{$t('messages.byUser')}{/if}
	</p>
	<p class="text-sm opacity-60">
		{allMessages.length} / {data.total}
	</p>
</div>

<!-- Message list -->
{#if allMessages.length === 0 && !loading}
	<p class="opacity-60">{$t('messages.noMessages')}</p>
{:else}
	<div class="space-y-1">
		{#each allMessages as msg (msg.event_id)}
			<div class="chat chat-start">
				{#if msg.sender?.avatar_url}
					<div class="chat-image avatar">
						<div class="w-8 rounded-full">
							<img src="/api/v1/avatars/users/{encodeURIComponent(msg.sender_id)}" alt="" loading="lazy" />
						</div>
					</div>
				{:else}
					<div class="chat-image avatar placeholder">
						<div class="bg-neutral text-neutral-content w-8 rounded-full">
							<span class="text-xs">{(msg.sender?.display_name || msg.sender_id || '?')[0]}</span>
						</div>
					</div>
				{/if}
				<div class="chat-header">
					<a href="/users/{encodeURIComponent(msg.sender_id)}" class="link link-hover font-medium">
						{msg.sender?.display_name || msg.sender_id}
					</a>
					<time class="text-xs opacity-50 ml-2">
						<Time timestamp={msg.timestamp} />
					</time>
				</div>
				<div class="chat-bubble">
					{msg.content}
					{#if msg.media && msg.media.length > 0}
						<div class="flex flex-wrap gap-2 mt-2">
							{#each msg.media as attachment}
								{#if attachment.mime_type && attachment.mime_type.startsWith('image/')}
									<a
										href="/api/v1/media/{attachment.media_id}/download"
										target="_blank"
										class="block max-w-48"
									>
										<img
											src="/api/v1/media/{attachment.media_id}/download"
											alt={attachment.original_filename || 'image'}
											class="rounded max-h-48 object-cover"
											loading="lazy"
										/>
									</a>
								{:else}
									<a
										href="/api/v1/media/{attachment.media_id}/download"
										class="flex items-center gap-2 bg-base-300 rounded px-3 py-2 text-sm hover:bg-base-100 transition-colors"
										target="_blank"
									>
										<span class="opacity-60">📎</span>
										<span class="truncate max-w-32">{attachment.original_filename || 'file'}</span>
										{#if attachment.size}
											<span class="text-xs opacity-50">
												{attachment.size > 1048576
													? `${(attachment.size / 1048576).toFixed(1)}MB`
													: `${Math.round(attachment.size / 1024)}KB`}
											</span>
										{/if}
									</a>
								{/if}
							{/each}
						</div>
					{/if}
				</div>
				<div class="chat-footer opacity-50">
					<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover text-xs">
						{msg.room?.name || msg.room_id}
					</a>
				</div>
			</div>
		{/each}
	</div>

	<InfiniteScroll {loading} {hasMore} onLoadMore={loadMore} />
{/if}
