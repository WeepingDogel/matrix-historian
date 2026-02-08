<script>
	import { goto } from '$app/navigation';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');

	function doSearch(e) {
		e.preventDefault();
		const params = new URLSearchParams();
		if (searchInput) params.set('q', searchInput);
		goto(`/messages?${params.toString()}`);
	}
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
<form onsubmit={doSearch} class="flex gap-2 mb-6">
	<input
		type="text"
		placeholder="Search messages…"
		class="input input-bordered flex-1"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">Search</button>
	{#if data.query}
		<a href="/messages" class="btn btn-ghost">Clear</a>
	{/if}
</form>

<p class="text-sm opacity-60 mb-4">
	{data.total.toLocaleString()} message{data.total !== 1 ? 's' : ''}
	{#if data.query}matching "<strong>{data.query}</strong>"{/if}
</p>

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
	<div class="flex gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a
				href="/messages?skip={Math.max(0, data.skip - 50)}{data.query ? `&q=${encodeURIComponent(data.query)}` : ''}"
				class="btn btn-outline btn-sm"
			>
				← Previous
			</a>
		{/if}
		{#if data.hasMore}
			<a
				href="/messages?skip={data.nextSkip}{data.query ? `&q=${encodeURIComponent(data.query)}` : ''}"
				class="btn btn-outline btn-sm"
			>
				Next →
			</a>
		{/if}
	</div>
{/if}
