<script>
	import Chart from '$lib/Chart.svelte';

	let { data } = $props();

	// Message trend chart data
	let trendLabels = $derived(data.messageStats.map((s) => s[0] ?? s.date ?? ''));
	let trendCounts = $derived(data.messageStats.map((s) => s[1] ?? s.count ?? 0));

	// User activity chart data
	let userLabels = $derived(data.userActivity.map((u) => u.display_name || u.user || ''));
	let userCounts = $derived(data.userActivity.map((u) => u.message_count));

	// Room activity chart data
	let roomLabels = $derived(data.roomActivity.map((r) => r.name || r.room || ''));
	let roomCounts = $derived(data.roomActivity.map((r) => r.message_count));
</script>

<svelte:head>
	<title>Analytics – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-6">Analytics</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<!-- Message Trends -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<h3 class="card-title text-lg">Message Trends (14 days)</h3>
			{#if trendLabels.length > 0}
				<Chart
					type="line"
					labels={trendLabels}
					datasets={[
						{
							label: 'Messages',
							data: trendCounts,
							borderColor: '#661ae6',
							backgroundColor: 'rgba(102,26,230,0.15)',
							fill: true,
							tension: 0.3
						}
					]}
				/>
			{:else}
				<p class="opacity-60">No data available.</p>
			{/if}
		</div>
	</div>

	<!-- User Activity -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<h3 class="card-title text-lg">Top Users</h3>
			{#if userLabels.length > 0}
				<Chart
					type="bar"
					labels={userLabels}
					datasets={[
						{
							label: 'Messages',
							data: userCounts,
							backgroundColor: '#1fb2a5'
						}
					]}
				/>
			{:else}
				<p class="opacity-60">No data available.</p>
			{/if}
		</div>
	</div>

	<!-- Room Activity -->
	<div class="card bg-base-200 shadow lg:col-span-2">
		<div class="card-body">
			<h3 class="card-title text-lg">Room Activity</h3>
			{#if roomLabels.length > 0}
				<Chart
					type="bar"
					labels={roomLabels}
					datasets={[
						{
							label: 'Messages',
							data: roomCounts,
							backgroundColor: '#d926a9'
						}
					]}
					options={{
						indexAxis: 'y'
					}}
				/>
			{:else}
				<p class="opacity-60">No data available.</p>
			{/if}
		</div>
	</div>
</div>
