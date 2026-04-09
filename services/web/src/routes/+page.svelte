<script>
	import Chart from '$lib/Chart.svelte';
	import AnimatedCount from '$lib/AnimatedCount.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import { getMessagesCount, getMessages, getUsers, getRooms, getAnalyticsOverview } from '$lib/api.js';
	import { onMount } from 'svelte';

	let { data } = $props();

	let pageLoading = $state(true);
	let messageCount = $state(0);
	let roomCount = $state(0);
	let userCount = $state(0);
	let recentMessages = $state([]);
	let rooms = $state([]);
	let users = $state([]);
	let overview = $state(null);

	let hourlyActivity = $derived(overview?.hourly_activity ?? []);
	let hourlyLabels = $derived(hourlyActivity.map((h) => `${String(h.hour ?? h[0] ?? '').padStart(2, '0')}:00`));
	let hourlyCounts = $derived(hourlyActivity.map((h) => h.count ?? h[1] ?? 0));

	async function fetchData() {
		try {
			const [countData, topRooms, topUsers, allRooms, allUsers, recent, overviewData] = await Promise.all([
				getMessagesCount({}),
				getRooms({ limit: 5 }),
				getUsers({ limit: 5 }),
				getRooms({ limit: 100000 }),
				getUsers({ limit: 100000 }),
				getMessages({ limit: 10 }),
				getAnalyticsOverview().catch(() => null)
			]);
			messageCount = countData.total ?? 0;
			roomCount = Array.isArray(allRooms) ? allRooms.length : 0;
			userCount = Array.isArray(allUsers) ? allUsers.length : 0;
			recentMessages = recent.messages ?? [];
			rooms = Array.isArray(topRooms) ? topRooms.slice(0, 5) : [];
			users = Array.isArray(topUsers) ? topUsers.slice(0, 5) : [];
			overview = overviewData;
		} catch (e) {
			console.error('Dashboard fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	onMount(() => {
		fetchData();
		const interval = setInterval(async () => {
			try {
				const [countData, recent, allRooms, allUsers] = await Promise.all([
					getMessagesCount({}),
					getMessages({ limit: 10 }),
					getRooms({ limit: 100000 }),
					getUsers({ limit: 100000 })
				]);
				messageCount = countData.total ?? messageCount;
				roomCount = Array.isArray(allRooms) ? allRooms.length : roomCount;
				userCount = Array.isArray(allUsers) ? allUsers.length : userCount;
				if (recent.messages?.length > 0) recentMessages = recent.messages;
			} catch {}
		}, 5000);
		return () => clearInterval(interval);
	});
</script>

<svelte:head>
	<title>{$t('dashboard.title')} – {$t('app.title')}</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-6">{$t('dashboard.title')}</h2>

<!-- Stats cards -->
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
	{#if pageLoading}
		<Skeleton variant="stat" count={3} />
	{:else}
		<a href="/messages" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
			<div class="stat-figure text-primary text-3xl">💬</div>
			<div class="stat-title">{$t('dashboard.totalMessages')}</div>
			<div class="stat-value text-primary"><AnimatedCount value={messageCount} /></div>
			<div class="stat-desc">{$t('dashboard.viewMessages')}</div>
		</a>
		<a href="/rooms" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
			<div class="stat-figure text-secondary text-3xl">🏠</div>
			<div class="stat-title">{$t('dashboard.rooms')}</div>
			<div class="stat-value text-secondary"><AnimatedCount value={roomCount} /></div>
			<div class="stat-desc">{$t('dashboard.browseRooms')}</div>
		</a>
		<a href="/users" class="stat bg-base-200 rounded-box shadow hover:bg-base-300 transition-colors cursor-pointer">
			<div class="stat-figure text-accent text-3xl">👥</div>
			<div class="stat-title">{$t('dashboard.users')}</div>
			<div class="stat-value text-accent"><AnimatedCount value={userCount} /></div>
			<div class="stat-desc">{$t('dashboard.viewUsers')}</div>
		</a>
	{/if}
</div>

<!-- Quick navigation cards -->
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
	<a href="/analytics" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">📈 {$t('dashboard.analytics')}</h3>
			<p class="text-xs opacity-60">{$t('dashboard.analyticsDesc')}</p>
		</div>
	</a>
	<a href="/media" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🖼️ {$t('dashboard.mediaGallery')}</h3>
			<p class="text-xs opacity-60">{$t('dashboard.mediaGalleryDesc')}</p>
		</div>
	</a>
	<a href="/messages?q=" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🔍 {$t('dashboard.searchMessages')}</h3>
			<p class="text-xs opacity-60">{$t('dashboard.searchMessagesDesc')}</p>
		</div>
	</a>
	<a href="/analytics#heatmap" class="card bg-base-200 shadow hover:bg-base-300 transition-colors">
		<div class="card-body p-4">
			<h3 class="card-title text-sm">🗓️ {$t('dashboard.activityHeatmap')}</h3>
			<p class="text-xs opacity-60">{$t('dashboard.activityHeatmapDesc')}</p>
		</div>
	</a>
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
	<!-- Recent messages -->
	<div class="card bg-base-200 shadow">
		<div class="card-body">
			<div class="flex justify-between items-center mb-2">
				<h3 class="card-title text-lg">{$t('dashboard.recentMessages')}</h3>
				<a href="/messages" class="btn btn-ghost btn-xs">{$t('common.viewAll')}</a>
			</div>
			{#if pageLoading}
				<Skeleton variant="chat" count={3} />
			{:else if recentMessages.length === 0}
				<p class="opacity-60">{$t('dashboard.noMessages')}</p>
			{:else}
				<div class="space-y-2 max-h-96 overflow-y-auto">
					{#each recentMessages as msg}
						<div class="chat chat-start">
							<div class="chat-header">
								<a href="/users/{encodeURIComponent(msg.sender_id)}" class="link link-hover font-medium text-sm">
									{msg.sender?.display_name || msg.sender_id}
								</a>
								<time class="text-xs opacity-50 ml-2">
									<Time timestamp={msg.timestamp} />
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
				<h3 class="card-title text-lg">{$t('dashboard.hourlyActivity')}</h3>
				<a href="/analytics" class="btn btn-ghost btn-xs">{$t('nav.analytics')} →</a>
			</div>
			{#if pageLoading}
				<div class="skeleton w-full h-64"></div>
			{:else if hourlyLabels.length > 0}
				<Chart
					type="bar"
					labels={hourlyLabels}
					datasets={[
						{
							label: $t('analytics.messages'),
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
				<p class="opacity-60">{$t('common.noData')}</p>
			{/if}
		</div>
	</div>
</div>

<!-- Quick lists -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
	{#if pageLoading}
		<Skeleton variant="card" count={2} />
	{:else}
		{#if rooms.length > 0}
			<div class="card bg-base-200 shadow">
				<div class="card-body">
					<div class="flex justify-between items-center mb-2">
						<h3 class="card-title text-lg">{$t('dashboard.rooms')}</h3>
						<a href="/rooms" class="btn btn-ghost btn-xs">{$t('common.viewAll')}</a>
					</div>
					<ul class="space-y-1">
						{#each rooms as room}
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
		{#if users.length > 0}
			<div class="card bg-base-200 shadow">
				<div class="card-body">
					<div class="flex justify-between items-center mb-2">
						<h3 class="card-title text-lg">{$t('dashboard.users')}</h3>
						<a href="/users" class="btn btn-ghost btn-xs">{$t('common.viewAll')}</a>
					</div>
					<ul class="space-y-1">
						{#each users as user}
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
	{/if}
</div>
