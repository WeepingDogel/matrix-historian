<script>
	let { data } = $props();
</script>

<svelte:head>
	<title>Dashboard – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-6">Dashboard</h2>

{#if data.error}
	<div class="alert alert-warning mb-4">
		<span>⚠️ Could not reach API: {data.error}</span>
	</div>
{/if}

<!-- Stats cards -->
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
	<div class="stat bg-base-200 rounded-box shadow">
		<div class="stat-title">Total Messages</div>
		<div class="stat-value text-primary">{data.messageCount.toLocaleString()}</div>
	</div>
	<div class="stat bg-base-200 rounded-box shadow">
		<div class="stat-title">Rooms</div>
		<div class="stat-value text-secondary">{data.roomCount}</div>
	</div>
	<div class="stat bg-base-200 rounded-box shadow">
		<div class="stat-title">Users</div>
		<div class="stat-value text-accent">{data.userCount}</div>
	</div>
</div>

<!-- Recent activity -->
<h3 class="text-lg font-semibold mb-3">Recent Messages</h3>

{#if data.recentMessages.length === 0}
	<p class="opacity-60">No messages yet.</p>
{:else}
	<div class="space-y-2">
		{#each data.recentMessages as msg}
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
				<div class="chat-footer opacity-50">
					<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover">
						{msg.room?.name || msg.room_id}
					</a>
				</div>
			</div>
		{/each}
	</div>
{/if}
