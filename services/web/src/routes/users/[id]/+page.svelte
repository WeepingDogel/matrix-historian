<script>
	let { data } = $props();

	let displayName = $derived(
		data.messages.length > 0
			? (data.messages[0].sender?.display_name || data.userId)
			: data.userId
	);

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);
</script>

<svelte:head>
	<title>{displayName} – Matrix Historian</title>
</svelte:head>

<div class="breadcrumbs text-sm mb-4">
	<ul>
		<li><a href="/users">Users</a></li>
		<li>{displayName}</li>
	</ul>
</div>

<h2 class="text-2xl font-bold mb-2">{displayName}</h2>
<p class="text-xs font-mono opacity-50 mb-2">{data.userId}</p>
<p class="text-sm opacity-60 mb-6">
	{data.total.toLocaleString()} message{data.total !== 1 ? 's' : ''}
	{#if data.total > 0}· Page {currentPage} of {totalPages}{/if}
</p>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

{#if data.messages.length === 0}
	<p class="opacity-60">No messages from this user.</p>
{:else}
	<div class="space-y-1">
		{#each data.messages as msg}
			<div class="chat chat-start">
				<div class="chat-header">
					<span class="font-medium">{displayName}</span>
					<time class="text-xs opacity-50 ml-2">
						{new Date(msg.timestamp).toLocaleString()}
					</time>
				</div>
				<div class="chat-bubble chat-bubble-secondary">{msg.content}</div>
				<div class="chat-footer opacity-50">
					<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover text-xs">
						{msg.room?.name || msg.room_id}
					</a>
				</div>
			</div>
		{/each}
	</div>

	<div class="flex items-center gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a href="/users/{encodeURIComponent(data.userId)}?skip={Math.max(0, data.skip - data.limit)}" class="btn btn-outline btn-sm">
				← Previous
			</a>
		{/if}
		<span class="text-sm opacity-60">Page {currentPage} / {totalPages}</span>
		{#if data.hasMore}
			<a href="/users/{encodeURIComponent(data.userId)}?skip={data.skip + data.limit}" class="btn btn-outline btn-sm">
				Next →
			</a>
		{/if}
	</div>
{/if}
