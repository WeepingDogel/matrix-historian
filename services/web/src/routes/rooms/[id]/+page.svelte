<script>
	let { data } = $props();

	let roomName = $derived(
		data.messages.length > 0 ? (data.messages[0].room?.name || data.roomId) : data.roomId
	);
</script>

<svelte:head>
	<title>{roomName} – Matrix Historian</title>
</svelte:head>

<div class="breadcrumbs text-sm mb-4">
	<ul>
		<li><a href="/rooms">Rooms</a></li>
		<li>{roomName}</li>
	</ul>
</div>

<h2 class="text-2xl font-bold mb-4">{roomName}</h2>
<p class="text-xs font-mono opacity-50 mb-6">{data.roomId}</p>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

{#if data.messages.length === 0}
	<p class="opacity-60">No messages in this room.</p>
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
				<div class="chat-bubble chat-bubble-primary">{msg.content}</div>
			</div>
		{/each}
	</div>

	<div class="flex gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a href="/rooms/{encodeURIComponent(data.roomId)}?skip={Math.max(0, data.skip - 100)}" class="btn btn-outline btn-sm">
				← Previous
			</a>
		{/if}
		{#if data.hasMore}
			<a href="/rooms/{encodeURIComponent(data.roomId)}?skip={data.skip + 100}" class="btn btn-outline btn-sm">
				Next →
			</a>
		{/if}
	</div>
{/if}
