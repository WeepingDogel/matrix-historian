<script>
	import Chart from '$lib/Chart.svelte';
	import { goto } from '$app/navigation';

	let { data } = $props();

	// Message trend chart data (14-day stats) — API returns {date, count} objects
	let trendLabels = $derived(data.messageStats.map((s) => {
		const raw = s.date ?? s[0] ?? '';
		// Try to format as short date
		try {
			const d = new Date(raw);
			return isNaN(d) ? String(raw) : `${d.getMonth() + 1}/${d.getDate()}`;
		} catch { return String(raw); }
	}));
	let trendCounts = $derived(data.messageStats.map((s) => s.count ?? s[1] ?? 0));

	// User activity chart data
	let userLabels = $derived(data.userActivity.map((u) => u.display_name || u.user || ''));
	let userCounts = $derived(data.userActivity.map((u) => u.message_count));

	// Room activity chart data
	let roomLabels = $derived(data.roomActivity.map((r) => r.name || r.room || ''));
	let roomCounts = $derived(data.roomActivity.map((r) => r.message_count));

	// Hourly activity — array of {hour, count} from overview endpoint
	let hourlyLabels = $derived((data.hourlyActivity ?? []).map((h) => `${String(h.hour ?? h[0] ?? '').padStart(2, '0')}:00`));
	let hourlyCounts = $derived((data.hourlyActivity ?? []).map((h) => h.count ?? h[1] ?? 0));

	// Trends with interval
	let trendsLabels = $derived(data.trends.map((t) => {
		const raw = t.period ?? t.date ?? t[0] ?? '';
		try {
			const d = new Date(raw);
			return isNaN(d) ? String(raw) : `${d.getMonth() + 1}/${d.getDate()}`;
		} catch { return String(raw); }
	}));
	let trendsTotals = $derived(data.trends.map((t) => t.count ?? t.total ?? t[1] ?? 0));

	// Word cloud - sort by count descending, take top 60
	let wordCloudData = $derived(
		[...(data.wordcloud ?? [])]
			.sort((a, b) => (b.count ?? 0) - (a.count ?? 0))
			.slice(0, 60)
	);
	let maxWordCount = $derived(wordCloudData.length > 0 ? wordCloudData[0].count : 1);

	// Heatmap - compute max for color scaling
	let heatmapMax = $derived(
		data.heatmap.length > 0
			? Math.max(...data.heatmap.flat().filter((v) => typeof v === 'number'), 1)
			: 1
	);

	// Interval selector
	let selectedInterval = $state(data.interval);
	function changeInterval() {
		goto(`/analytics?interval=${selectedInterval}`);
	}

	function heatmapColor(value) {
		if (!value || value === 0) return 'bg-base-300 opacity-30';
		const intensity = value / heatmapMax;
		if (intensity > 0.75) return 'bg-primary text-primary-content';
		if (intensity > 0.5) return 'bg-primary/70 text-primary-content';
		if (intensity > 0.25) return 'bg-primary/40';
		return 'bg-primary/20';
	}
</script>

<svelte:head>
	<title>Analytics – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-6">Analytics</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

<!-- Overview stats -->
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
	<div class="stat bg-base-200 rounded-box shadow p-3">
		<div class="stat-title text-xs">Total Messages</div>
		<div class="stat-value text-lg text-primary">{(data.totalMessages ?? 0).toLocaleString()}</div>
	</div>
	<div class="stat bg-base-200 rounded-box shadow p-3">
		<div class="stat-title text-xs">Total Rooms</div>
		<div class="stat-value text-lg text-secondary">{(data.totalRooms ?? 0).toLocaleString()}</div>
	</div>
	<div class="stat bg-base-200 rounded-box shadow p-3">
		<div class="stat-title text-xs">Total Users</div>
		<div class="stat-value text-lg text-accent">{(data.totalUsers ?? 0).toLocaleString()}</div>
	</div>
	<div class="stat bg-base-200 rounded-box shadow p-3">
		<div class="stat-title text-xs">Avg/Day (14d)</div>
		<div class="stat-value text-lg">{(data.avgPerDay ?? 0).toLocaleString()}</div>
	</div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
	<!-- Message Trends (14 days) -->
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

	<!-- Trends with interval selector -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<div class="flex justify-between items-center">
				<h3 class="card-title text-lg">Trends</h3>
				<div class="flex gap-1">
					<select class="select select-bordered select-xs" bind:value={selectedInterval} onchange={changeInterval}>
						<option value="hour">Hourly</option>
						<option value="day">Daily</option>
						<option value="week">Weekly</option>
					</select>
				</div>
			</div>
			{#if trendsLabels.length > 0}
				<Chart
					type="bar"
					labels={trendsLabels}
					datasets={[
						{
							label: `Messages (${selectedInterval})`,
							data: trendsTotals,
							backgroundColor: 'rgba(102,26,230,0.6)',
							borderRadius: 4
						}
					]}
				/>
			{:else}
				<p class="opacity-60">No trend data available.</p>
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

	<!-- Hourly Activity -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<h3 class="card-title text-lg">Hourly Activity</h3>
			{#if hourlyLabels.length > 0}
				<Chart
					type="bar"
					labels={hourlyLabels}
					datasets={[
						{
							label: 'Messages',
							data: hourlyCounts,
							backgroundColor: 'rgba(217,38,169,0.6)',
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

	<!-- Activity Heatmap -->
	<div id="heatmap" class="card bg-base-200 shadow lg:col-span-2">
		<div class="card-body">
			<h3 class="card-title text-lg">Activity Heatmap</h3>
			<p class="text-xs opacity-60 mb-2">Messages by day of week and hour</p>
			{#if data.heatmap.length > 0}
				<div class="overflow-x-auto">
					<table class="table table-xs">
						<thead>
							<tr>
								<th class="text-xs w-16"></th>
								{#each data.heatmapHours as hour}
									<th class="text-xs text-center p-1">{String(hour).padStart(2, '0')}</th>
								{/each}
							</tr>
						</thead>
						<tbody>
							{#each data.heatmap as row, dayIdx}
								<tr>
									<td class="text-xs font-medium">{data.heatmapWeekdays[dayIdx] ?? dayIdx}</td>
									{#each row as value}
										<td class="p-0">
											<div
												class="w-full h-6 flex items-center justify-center text-[10px] rounded-sm {heatmapColor(value)}"
												title="{value} messages"
											>
												{#if value > 0}{value}{/if}
											</div>
										</td>
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{:else}
				<p class="opacity-60">No heatmap data available.</p>
			{/if}
		</div>
	</div>

	<!-- Word Cloud -->
	<div class="card bg-base-200 shadow lg:col-span-2">
		<div class="card-body">
			<h3 class="card-title text-lg">Word Cloud</h3>
			{#if wordCloudData.length > 0}
				<div class="flex flex-wrap gap-2 justify-center py-4">
					{#each wordCloudData as item}
						{@const ratio = (item.count ?? 1) / maxWordCount}
						{@const fontSize = Math.max(0.7, ratio * 2.5)}
						<span
							class="inline-block transition-transform hover:scale-110 cursor-default"
							style="font-size: {fontSize}rem; opacity: {Math.max(0.4, ratio)}"
							title="{item.word}: {item.count} occurrences"
						>
							{item.word}
						</span>
					{/each}
				</div>
			{:else}
				<p class="opacity-60">No word cloud data available.</p>
			{/if}
		</div>
	</div>

	<!-- User Interactions -->
	{#if data.interactions.length > 0}
		<div class="card bg-base-200 shadow lg:col-span-2">
			<div class="card-body">
				<h3 class="card-title text-lg">User Interactions</h3>
				<div class="overflow-x-auto max-h-64 overflow-y-auto">
					<table class="table table-xs">
						<thead>
							<tr>
								<th>Room</th>
								<th>User</th>
								<th>Time</th>
							</tr>
						</thead>
						<tbody>
							{#each data.interactions.slice(0, 30) as row}
								<tr>
									<td class="text-xs">{row.room_id ?? ''}</td>
									<td class="text-xs">{row.sender_id ?? ''}</td>
									<td class="text-xs opacity-60">{row.timestamp ?? ''}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	{/if}
</div>
