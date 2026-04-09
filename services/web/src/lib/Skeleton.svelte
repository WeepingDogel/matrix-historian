<script>
	let { variant = 'card', count = 1 } = $props();
</script>

{#each Array(count) as _, i}
	{#if variant === 'stat'}
		<div class="stat bg-base-200 rounded-box shadow p-3">
			<div class="skeleton h-3 w-16 mb-2"></div>
			<div class="skeleton h-6 w-24"></div>
		</div>
	{:else if variant === 'chart'}
		<div class="card bg-base-200 shadow">
			<div class="card-body">
				<div class="skeleton h-5 w-40 mb-4"></div>
				<div class="skeleton w-full h-64"></div>
			</div>
		</div>
	{:else if variant === 'chat'}
		<div class="chat {i % 2 === 0 ? 'chat-start' : 'chat-end'}">
			<div class="chat-image avatar">
				<div class="skeleton w-10 h-10 rounded-full"></div>
			</div>
			<div class="chat-header">
				<div class="skeleton h-3 w-24 mb-1"></div>
			</div>
			<div class="chat-bubble bg-base-300">
				<div class="skeleton h-3 w-48 mb-1"></div>
				<div class="skeleton h-3 w-32"></div>
			</div>
		</div>
	{:else if variant === 'table-row'}
		<tr>
			<td><div class="skeleton h-4 w-32"></div></td>
			<td><div class="skeleton h-4 w-24"></div></td>
			<td><div class="skeleton h-4 w-16"></div></td>
		</tr>
	{:else if variant === 'media'}
		<div class="skeleton w-full h-40 rounded-box"></div>
	{:else}
		<!-- card -->
		<div class="card bg-base-200 shadow">
			<div class="card-body">
				<div class="skeleton h-5 w-40 mb-3"></div>
				<div class="skeleton h-4 w-full mb-2"></div>
				<div class="skeleton h-4 w-3/4"></div>
			</div>
		</div>
	{/if}
{/each}
