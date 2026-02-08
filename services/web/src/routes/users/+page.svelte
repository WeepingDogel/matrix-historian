<script>
	let { data } = $props();
</script>

<svelte:head>
	<title>Users – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Users</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

{#if data.users.length === 0}
	<p class="opacity-60">No users found.</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>Display Name</th>
					<th>User ID</th>
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
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
