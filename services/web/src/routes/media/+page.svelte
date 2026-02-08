<script>
	let { data } = $props();

	const filters = [
		{ label: 'All', value: '' },
		{ label: 'Images', value: 'image/' },
		{ label: 'Videos', value: 'video/' },
		{ label: 'Audio', value: 'audio/' }
	];

	function isImage(mime) {
		return mime && mime.startsWith('image/');
	}

	function formatSize(bytes) {
		if (!bytes) return '—';
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}
</script>

<svelte:head>
	<title>Media – Matrix Historian</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">Media Gallery</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>⚠️ {data.error}</span></div>
{/if}

<!-- Filter tabs -->
<div class="tabs tabs-box mb-6">
	{#each filters as f}
		<a
			href="/media?type={f.value}"
			class="tab"
			class:tab-active={data.mimeFilter === f.value}
		>
			{f.label}
		</a>
	{/each}
</div>

<p class="text-sm opacity-60 mb-4">{data.total.toLocaleString()} file{data.total !== 1 ? 's' : ''}</p>

{#if data.media.length === 0}
	<p class="opacity-60">No media found.</p>
{:else}
	<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
		{#each data.media as m}
			<div class="card bg-base-200 shadow-sm">
				<figure class="h-32 bg-base-300 flex items-center justify-center overflow-hidden">
					{#if isImage(m.mime_type)}
						<img
							src="/api/v1/media/{m.media_id}/download"
							alt={m.original_filename || 'media'}
							class="object-cover w-full h-full"
							loading="lazy"
						/>
					{:else}
						<span class="text-3xl opacity-40">📄</span>
					{/if}
				</figure>
				<div class="card-body p-3">
					<p class="text-xs truncate" title={m.original_filename}>
						{m.original_filename || 'untitled'}
					</p>
					<p class="text-xs opacity-50">{formatSize(m.size)}</p>
				</div>
			</div>
		{/each}
	</div>

	<!-- Pagination -->
	<div class="flex gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a href="/media?skip={Math.max(0, data.skip - 48)}&type={data.mimeFilter}" class="btn btn-outline btn-sm">
				← Previous
			</a>
		{/if}
		{#if data.hasMore}
			<a href="/media?skip={data.nextSkip}&type={data.mimeFilter}" class="btn btn-outline btn-sm">
				Next →
			</a>
		{/if}
	</div>
{/if}
