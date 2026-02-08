<script>
	import Chart from '$lib/Chart.svelte';

	let { data } = $props();

	// Hourly activity from overview
	let hourlyActivity = $derived(data.overview?.hourly_activity ?? []);
	let hourlyLabels = $derived(hourlyActivity.map((h) => `${String(h.hour ?? h[0] ?? '').padStart(2, '0')}:00`));
	let hourlyCounts = $derived(hourlyActivity.map((h) => h.count ?? h[1] ?? 0));
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
	<a href="/messages" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
		<div class="stat-figure text-primary text-3xl">💬</div>
		<div class="stat-title">Total Messages</div>
		<div class="stat-value text-primary">{data.messageCount.toLocaleString()}</div>
		<div class="stat-desc">View all messages →</div>
	</a>
	<a href="/rooms" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
		<div class="stat-figure text-secondary text-3xl">🏠</div>
		<div class="stat-title">Rooms</div>
		<div class="stat-value text-secondary">{data.roomCount}</div>
		<div class="stat-desc">Browse rooms →</div>
	</a>
	<a href="/users" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
		<div class="stat-figure text-accent text-3xl">👥</div>
		<div class="stat-title">Users</div>
		<div class="stat-value text-accent">{data.userCount}</div>
		<div class="stat-desc">View users →</div>
	</a>
</div>

<!-- Quick navigation cards -->
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
	<a href="/analytics" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">📈 Analytics</h3>
			<p class="text-xs opacity-60">Charts, trends & insights</p>
		</div>
	</a>
	<a href="/media" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🖼️ Media Gallery</h3>
			<p class="text-xs opacity-60">Browse shared files</p>
		</div>
	</a>
	<a href="/messages?q=" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🔍 Search Messages</h3>
			<p class="text-xs opacity-60">Full-text search</p>
		</div>
	</a>
	<a href="/analytics#heatmap" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🗓️ Activity Heatmap</h3>
			<p class="text-xs opacity-60">When is the server active?</p>
		</div>
	</a>
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
	<!-- Recent messages -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<div class="flex justify-between items-center mb-2">
				<h3 class="card-title text-lg">Recent Messages</h3>
				<a href="/messages" class="btn btn-ghost btn-xs">View all →</a>
			</div>

			{#if data.recentMessages.length === 0}
				<p class="opacity-60">No messages yet.</p>
			{:else}
				<div class="space-y-2 max-h-96 overflow-y-auto">
					{#each data.recentMessages as msg}
						<div class="chat chat-start">
							<div class="chat-header">
								<a href="/users/{encodeURIComponent(msg.sender_id)}" class="link link-hover font-medium text-sm">
									{msg.sender?.display_name || msg.sender_id}
								</a>
								<time class="text-xs opacity-50 ml-2">
									{new Date(msg.timestamp).toLocaleString()}
								</time>
							</div>
							<div class="chat-bubble chat-bubble-primary text-sm">{msg.content}</div>
							<div class="chat-footer opacity-50">
								<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover text-xs">
									{msg.room?.name || msg.room_id}
								</a>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<!-- Hourly activity chart -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<div class="flex justify-between items-center mb-2">
				<h3 class="card-title text-lg">Hourly Activity</h3>
				<a href="/analytics" class="btn btn-ghost btn-xs">Analytics →</a>
			</div>
			{#if hourlyLabels.length > 0}
				<Chart
					type="bar"
					labels={hourlyLabels}
					datasets={[
						{
							label: 'Messages',
							data: hourlyCounts,
							backgroundColor: 'rgba(102,26,230,0.6)',
							borderRadius: 4
						}
					]}
					options={{
						scales: { x: { ticks: { maxRotation: 45 } } }
					}}
				/>
			{:else}
				<p class="opacity-60">No hourly data available.</p>
			{/if}
		</div>
	</div>
</div>

<!-- Quick lists -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
	<!-- Top rooms -->
	{#if data.rooms.length > 0}
		<div class="card bg-base-200 shadow">
			<div class="card-body">
				<div class="flex justify-between items-center mb-2">
					<h3 class="card-title text-lg">Rooms</h3>
					<a href="/rooms" class="btn btn-ghost btn-xs">View all →</a>
				</div>
				<ul class="space-y-1">
					{#each data.rooms as room}
						<li>
							<a href="/rooms/{encodeURIComponent(room.room_id)}" class="link link-hover text-sm flex items-center gap-2">
								<span class="badge badge-sm badge-outline">🏠</span>
								{room.name || room.room_id}
							</a>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	{/if}

	<!-- Top users -->
	{#if data.users.length > 0}
		<div class="card bg-base-200 shadow">
			<div class="card-body">
				<div class="flex justify-between items-center mb-2">
					<h3 class="card-title text-lg">Users</h3>
					<a href="/users" class="btn btn-ghost btn-xs">View all →</a>
				</div>
				<ul class="space-y-1">
					{#each data.users as user}
						<li>
							<a href="/users/{encodeURIComponent(user.user_id)}" class="link link-hover text-sm flex items-center gap-2">
								<span class="badge badge-sm badge-outline">👤</span>
								{user.display_name || user.user_id}
							</a>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	{/if}
</div>
