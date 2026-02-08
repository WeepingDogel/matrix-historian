<script>
	let { data } = $props();
</script>

<svelte:head>
	<title>Rooms – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Rooms</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

{#if data.rooms.length === 0}
	<p class="opacity-60">No rooms found.</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>Name</th>
					<th>Room ID</th>
				</tr>
			</thead>
			<tbody>
				{#each data.rooms as room}
					<tr class="hover">
						<td>
							<a href="/rooms/{encodeURIComponent(room.room_id)}" class="link link-hover font-medium">
								{room.name || '(unnamed)'}
							</a>
						</td>
						<td class="font-mono text-xs opacity-70">{room.room_id}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
