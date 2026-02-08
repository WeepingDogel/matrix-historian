<script>
	import { goto } from '$app/navigation';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');
	let selectedRoom = $state(data.room_id ?? '');
	let selectedUser = $state(data.user_id ?? '');

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);

	function buildParams(overrides = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchInput;
		const room = overrides.room_id ?? selectedRoom;
		const user = overrides.user_id ?? selectedUser;
		const skip = overrides.skip ?? 0;
		if (q) params.set('q', q);
		if (room) params.set('room_id', room);
		if (user) params.set('user_id', user);
		if (skip > 0) params.set('skip', String(skip));
		return params.toString();
	}

	function doSearch(e) {
		e.preventDefault();
		goto(`/messages?${buildParams()}`);
	}

	function onFilterChange() {
		goto(`/messages?${buildParams({ skip: 0 })}`);
	}

	function clearFilters() {
		searchInput = '';
		selectedRoom = '';
		selectedUser = '';
		goto('/messages');
	}

	let hasFilters = $derived(data.query || data.room_id || data.user_id);
</script>

<svelte:head>
	<title>Messages – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Messages</h2>

{#if data.error}
	<div class="alert alert-warning mb-4">
		<span>⚠️ {data.error}</span>
	</div>
{/if}

<!-- Search bar -->
<form onsubmit={doSearch} class="flex flex-wrap gap-2 mb-4">
	<input
		type="text"
		placeholder="Search messages…"
		class="input input-bordered flex-1 min-w-48"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">Search</button>
	{#if hasFilters}
		<button type="button" class="btn btn-ghost" onclick={clearFilters}>Clear All</button>
	{/if}
</form>

<!-- Filters -->
<div class="flex flex-wrap gap-2 mb-6">
	<select class="select select-bordered select-sm" bind:value={selectedRoom} onchange={onFilterChange}>
		<option value="">All Rooms</option>
		{#each data.rooms as room}
			<option value={room.room_id}>{room.name || room.room_id}</option>
		{/each}
	</select>
	<select class="select select-bordered select-sm" bind:value={selectedUser} onchange={onFilterChange}>
		<option value="">All Users</option>
		{#each data.users as user}
			<option value={user.user_id}>{user.display_name || user.user_id}</option>
		{/each}
	</select>
</div>

<div class="flex justify-between items-center mb-4">
	<p class="text-sm opacity-60">
		{data.total.toLocaleString()} message{data.total !== 1 ? 's' : ''}
		{#if data.query}matching "<strong>{data.query}</strong>"{/if}
		{#if data.room_id}in room{/if}
		{#if data.user_id}by user{/if}
	</p>
	<p class="text-sm opacity-60">
		Page {currentPage} of {totalPages}
	</p>
</div>

<!-- Message list -->
{#if data.messages.length === 0}
	<p class="opacity-60">No messages found.</p>
{:else}
	<div class="space-y-1">
		{#each data.messages as msg}
			<div class="chat chat-start">
				<div class="chat-header">
					<a href="/users/{encodeURIComponent(msg.sender_id)}" class="link link-hover font-medium">
						{msg.sender?.display_name || msg.sender_id}
					</a>
					<time class="text-xs opacity-50 ml-2">
						{new Date(msg.timestamp).toLocaleString()}
					</time>
				</div>
				<div class="chat-bubble">{msg.content}</div>
				<div class="chat-footer opacity-50">
					<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover text-xs">
						{msg.room?.name || msg.room_id}
					</a>
				</div>
			</div>
		{/each}
	</div>

	<!-- Pagination -->
	<div class="flex items-center gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a
				href="/messages?{buildParams({ skip: Math.max(0, data.skip - data.limit) })}"
				class="btn btn-outline btn-sm"
			>
				← Previous
			</a>
		{/if}
		<span class="text-sm opacity-60">Page {currentPage} / {totalPages}</span>
		{#if data.hasMore}
			<a
				href="/messages?{buildParams({ skip: data.nextSkip })}"
				class="btn btn-outline btn-sm"
			>
				Next →
			</a>
		{/if}
	</div>
{/if}
