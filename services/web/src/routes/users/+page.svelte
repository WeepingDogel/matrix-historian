<script>
	import { goto } from '$app/navigation';

	let { data } = $props();
	let searchInput = $state(data.query ?? '');

	function doSearch(e) {
		e.preventDefault();
		const params = new URLSearchParams();
		if (searchInput.trim()) params.set('q', searchInput.trim());
		goto(`/users?${params.toString()}`);
	}
</script>

<svelte:head>
	<title>Users – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Users</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

<!-- Search -->
<form onsubmit={doSearch} class="flex gap-2 mb-6">
	<input
		type="text"
		placeholder="Search users…"
		class="input input-bordered flex-1 max-w-md"
		bind:value={searchInput}
	/>
	<button class="btn btn-primary" type="submit">Search</button>
	{#if data.query}
		<a href="/users" class="btn btn-ghost">Clear</a>
	{/if}
</form>

<p class="text-sm opacity-60 mb-4">
	{data.users.length} user{data.users.length !== 1 ? 's' : ''}
	{#if data.query}matching "<strong>{data.query}</strong>"{/if}
</p>

{#if data.users.length === 0}
	<p class="opacity-60">No users found.</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>Display Name</th>
					<th>User ID</th>
					<th class="text-right">Messages</th>
				</tr>
			</thead>
			<tbody>
				{#each data.users as user}
					<tr class="hover">
						<td>
							<a href="/users/{encodeURIComponent(user.user_id)}" class="link link-hover font-medium">
								{user.display_name || '(no display name)'}
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
{/if}
