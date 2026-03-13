<script>
	import { t } from '$lib/i18n';

	let { data } = $props();

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);

	function isImage(mime) {
		return mime && mime.startsWith('image/');
	}

	function isVideo(mime) {
		return mime && mime.startsWith('video/');
	}

	function isAudio(mime) {
		return mime && mime.startsWith('audio/');
	}

	function formatSize(bytes) {
		if (!bytes) return '—';
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	function mimeIcon(mime) {
		if (!mime) return '📄';
		if (mime.startsWith('image/')) return '🖼️';
		if (mime.startsWith('video/')) return '🎬';
		if (mime.startsWith('audio/')) return '🎵';
		if (mime.startsWith('text/')) return '📝';
		if (mime.includes('pdf')) return '📕';
		return '📄';
	}

	let filterItems = $derived([
		{ label: $t('media.all'), value: '', icon: '📁' },
		{ label: $t('media.images'), value: 'image/', icon: '🖼️' },
		{ label: $t('media.videos'), value: 'video/', icon: '🎬' },
		{ label: $t('media.audio'), value: 'audio/', icon: '🎵' }
	]);
</script>

<svelte:head>
	<title>{$t('media.title')} – {$t('app.title')}</title>
</svelte:head>

<h2 class="text-2xl font-bold mb-4">{$t('media.title')}</h2>

{#if data.error}
	<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
{/if}

<!-- Media stats -->
{#if data.stats}
	<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
		<div class="stat bg-base-200 rounded-box shadow p-3">
			<div class="stat-title text-xs">{$t('media.totalFiles')}</div>
			<div class="stat-value text-lg">{(data.stats.total_count ?? data.stats.total ?? 0).toLocaleString()}</div>
		</div>
		<div class="stat bg-base-200 rounded-box shadow p-3">
			<div class="stat-title text-xs">{$t('media.totalSize')}</div>
			<div class="stat-value text-lg">{formatSize(data.stats.total_size ?? 0)}</div>
		</div>
		{#if data.stats.breakdown}
			{#each Object.entries(data.stats.breakdown).slice(0, 2) as [type, count]}
				<div class="stat bg-base-200 rounded-box shadow p-3">
					<div class="stat-title text-xs">{type}</div>
					<div class="stat-value text-lg">{count.toLocaleString()}</div>
				</div>
			{/each}
		{/if}
	</div>
{/if}

<!-- Filter tabs -->
<div class="tabs tabs-box mb-6">
	{#each filterItems as f}
		<a
			href="/media?type={f.value}"
			class="tab"
			class:tab-active={data.mimeFilter === f.value}
		>
			<span class="mr-1">{f.icon}</span>
			{f.label}
		</a>
	{/each}
</div>

<div class="flex justify-between items-center mb-4">
	<p class="text-sm opacity-60">{$t('media.fileCount', { count: data.total.toLocaleString() })}</p>
	<p class="text-sm opacity-60">{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}</p>
</div>

{#if data.media.length === 0}
	<p class="opacity-60">{$t('media.noMedia')}</p>
{:else}
	<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
		{#each data.media as m}
			<div class="card bg-base-200 shadow-sm hover:shadow-md transition-shadow">
				<figure class="h-32 bg-base-300 flex items-center justify-center overflow-hidden relative">
					{#if isImage(m.mime_type)}
						<img
							src="/api/v1/media/{m.media_id}/download"
							alt={m.original_filename || 'media'}
							class="object-cover w-full h-full"
							loading="lazy"
						/>
					{:else if isVideo(m.mime_type)}
						<span class="text-4xl">🎬</span>
					{:else if isAudio(m.mime_type)}
						<span class="text-4xl">🎵</span>
					{:else}
						<span class="text-4xl">{mimeIcon(m.mime_type)}</span>
					{/if}
					<!-- Type badge -->
					<span class="absolute top-1 right-1 badge badge-xs badge-neutral opacity-80">
						{m.mime_type?.split('/')[0] ?? '?'}
					</span>
				</figure>
				<div class="card-body p-3">
					<p class="text-xs truncate font-medium" title={m.original_filename}>
						{m.original_filename || $t('media.untitled')}
					</p>
					<div class="flex justify-between items-center">
						<p class="text-xs opacity-50">{formatSize(m.size)}</p>
						<a
							href="/api/v1/media/{m.media_id}/download"
							target="_blank"
							rel="noopener noreferrer"
							class="btn btn-ghost btn-xs"
							title={$t('common.download')}
						>
							⬇️
						</a>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Pagination -->
	<div class="flex items-center gap-2 mt-6 justify-center">
		{#if data.skip > 0}
			<a href="/media?skip={Math.max(0, data.skip - data.limit)}&type={data.mimeFilter}" class="btn btn-outline btn-sm">
				{$t('common.previous')}
			</a>
		{/if}
		<span class="text-sm opacity-60">{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}</span>
		{#if data.hasMore}
			<a href="/media?skip={data.nextSkip}&type={data.mimeFilter}" class="btn btn-outline btn-sm">
				{$t('common.next')}
			</a>
		{/if}
	</div>
{/if}
