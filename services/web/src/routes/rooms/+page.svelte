<script>
	let { data } = $props();
	let searchQuery = $state('');

	let filteredRooms = $derived(
		searchQuery.trim()
			? data.rooms.filter((r) => {
					const q = searchQuery.toLowerCase();
					return (
						(r.name && r.name.toLowerCase().includes(q)) ||
						r.room_id.toLowerCase().includes(q)
					);
				})
			: data.rooms
	);
</script>

<svelte:head>
	<title>Rooms – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Rooms</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

<!-- Search -->
<div class="mb-6">
	<input
		type="text"
		placeholder="Filter rooms…"
		class="input input-bordered w-full max-w-md"
		bind:value={searchQuery}
	/>
</div>

<p class="text-sm opacity-60 mb-4">{filteredRooms.length} room{filteredRooms.length !== 1 ? 's' : ''}</p>

{#if filteredRooms.length === 0}
	<p class="opacity-60">No rooms found.</p>
{:else}
	<div class="overflow-x-auto">
		<table class="table table-zebra">
			<thead>
				<tr>
					<th>Name</th>
					<th>Room ID</th>
					<th class="text-right">Messages</th>
				</tr>
			</thead>
			<tbody>
				{#each filteredRooms as room}
					<tr class="hover">
						<td>
							<a href="/rooms/{encodeURIComponent(room.room_id)}" class="link link-hover font-medium">
								{room.name || '(unnamed)'}
							</a>
						</td>
						<td class="font-mono text-xs opacity-70">{room.room_id}</td>
						<td class="text-right">
							{#if data.activityMap[room.room_id] !== undefined}
								<span class="badge badge-sm">{data.activityMap[room.room_id].toLocaleString()}</span>
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
