<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import InfiniteScroll from '$lib/InfiniteScroll.svelte';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');

	// Accumulated items for infinite scroll
	let allUsers = $state([...data.users]);
	let currentSkip = $state(data.skip + data.users.length);
	let hasMore = $state(data.hasMore);
	let loading = $state(false);

	$effect(() => {
		allUsers = [...data.users];
		currentSkip = data.skip + data.users.length;
		hasMore = data.hasMore;
		loading = false;
	});

	function doSearch(e) {
		e.preventDefault();
		const params = new URLSearchParams();
		if (searchInput.trim()) params.set('q', searchInput.trim());
		goto(`/users?${params.toString()}`);
	}

	async function loadMore() {
		if (loading || !hasMore) return;
		loading = true;
		try {
			const apiParams = new URLSearchParams();
			apiParams.set('skip', String(currentSkip));
			apiParams.set('limit', String(data.limit));

			const endpoint = data.query
				? `/api/v1/users/search?query=${encodeURIComponent(data.query)}&${apiParams.toString()}`
				: `/api/v1/users?${apiParams.toString()}`;

			const res = await fetch(endpoint);
			if (!res.ok) throw new Error(`API ${res.status}`);
			const newUsers = await res.json();

			allUsers = [...allUsers, ...newUsers];
			currentSkip += newUsers.length;
			hasMore = newUsers.length >= data.limit;
		} catch (e) {
			console.error('Load more error:', e);
			hasMore = false;
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{$t('users.title')} – {$t('app.title')}</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">{$t('users.title')}</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
{/if}

<!-- Search -->
<form onsubmit={doSearch} class="flex gap-2 mb-6">
	<input
		type="text"
		placeholder={$t('users.searchPlaceholder')}
		class="input input-bordered flex-1 max-w-md"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">{$t('common.search')}</button>
	{#if data.query}
		<a href="/users" class="btn btn-ghost">{$t('common.clear')}</a>
	{/if}
</form>

<div class="flex justify-between items-center mb-4">
	<p class="text-sm opacity-60">
		{$t('users.userCount', { count: data.total })}
		{#if data.query}{$t('messages.matching', { query: data.query })}{/if}
	</p>
	<p class="text-sm opacity-60">
		{allUsers.length} / {data.total}
	</p>
</div>

{#if allUsers.length === 0 && !loading}
	<p class="opacity-60">{$t('users.noUsers')}</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>{$t('users.displayName')}</th>
					<th>{$t('users.userId')}</th>
					<th class="text-right">{$t('users.messagesCol')}</th>
				</tr>
			</thead>
			<tbody>
				{#each allUsers as user (user.user_id)}
					<tr class="hover">
						<td>
							<a href="/users/{encodeURIComponent(user.user_id)}" class="link link-hover font-medium">
								{user.display_name || $t('common.noDisplayName')}
							</a>
						</td>
						<td class="font-mono text-xs opacity-70">{user.user_id}</td>
						<td class="text-right">
							{#if data.activityMap[user.user_id] !== undefined}
								<span class="badge badge-sm">{data.activityMap[user.user_id].toLocaleString()}</span>
							{:else}
								<span class="opacity-40">—</span>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<InfiniteScroll {loading} {hasMore} onLoadMore={loadMore} />
{/if}
