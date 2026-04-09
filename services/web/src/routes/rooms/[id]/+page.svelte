<script>
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import { getRoomMessages, getMessagesCount } from '$lib/api.js';

	let { data } = $props();
	let pageLoading = $state(true);

	let roomName = $derived(
		data.messages.length > 0 ? (data.messages[0].room?.name || data.roomId) : data.roomId
	);

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);

	async function fetchRoomMessages() {
		pageLoading = true;
		try {
			const [messages, countData] = await Promise.all([
				getRoomMessages(data.roomId, { skip: data.skip, limit: data.limit }),
				getMessagesCount({ room_id: data.roomId }).catch(() => ({ total: 0 }))
			]);
			data = {
				...data,
				messages,
				total: countData.total ?? 0,
				hasMore: messages.length === data.limit,
				_loading: false
			};
		} catch (e) {
			console.error('Room detail fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	let lastFetchKey = '';
	$effect(() => {
		const key = `${data.roomId}|${data.skip}`;
		if (key === lastFetchKey) return;
		lastFetchKey = key;
		fetchRoomMessages();
	});
</script>

<svelte:head>
	<title>{roomName} – {$t('app.title')}</title>
</svelte:head>

<div class="breadcrumbs text-sm mb-4">
	<ul>
		<li><a href="/rooms">{$t('rooms.title')}</a></li>
		<li>{roomName}</li>
	</ul>
</div>

<h2 class="text-2xl font-bold mb-2">{roomName}</h2>
<p class="text-xs font-mono opacity-50 mb-2">{data.roomId}</p>

{#if pageLoading}
	<div class="space-y-3">
		<Skeleton variant="chat" count={5} />
	</div>
{:else}
	<p class="text-sm opacity-60 mb-6">
		{$t('rooms.messageCount', { count: data.total.toLocaleString() })}
		{#if data.total > 0}· {$t('common.page')} {currentPage} {$t('common.of')} {totalPages}{/if}
	</p>

	{#if data.error}
		<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
	{/if}

	{#if data.messages.length === 0}
		<p class="opacity-60">{$t('messages.noMessages')}</p>
	{:else}
		<div class="space-y-1">
			{#each data.messages as msg}
				<div class="chat chat-start">
					<div class="chat-header">
						<a href="/users/{encodeURIComponent(msg.sender_id)}" class="link link-hover font-medium">
							{msg.sender?.display_name || msg.sender_id}
						</a>
						<time class="text-xs opacity-50 ml-2">
							<Time timestamp={msg.timestamp} />
						</time>
					</div>
					<div class="chat-bubble chat-bubble-primary">{msg.content}</div>
				</div>
			{/each}
		</div>

		<div class="flex items-center gap-2 mt-6 justify-center">
			{#if data.skip > 0}
				<a href="/rooms/{encodeURIComponent(data.roomId)}?skip={Math.max(0, data.skip - data.limit)}" class="btn btn-outline btn-sm">
					{$t('common.previous')}
				</a>
			{/if}
			<span class="text-sm opacity-60">{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}</span>
			{#if data.hasMore}
				<a href="/rooms/{encodeURIComponent(data.roomId)}?skip={data.skip + data.limit}" class="btn btn-outline btn-sm">
					{$t('common.next')}
				</a>
			{/if}
		</div>
	{/if}
{/if}
