<script>
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import InfiniteScroll from '$lib/InfiniteScroll.svelte';
	import { getRoomMessages, getMessagesCount } from '$lib/api.js';

	let { data } = $props();
	let pageLoading = $state(true);

	let roomName = $derived(
		data.messages.length > 0 ? (data.messages[0].room?.name || data.roomId) : data.roomId
	);

	// Accumulated messages for infinite scroll
	let allMessages = $state([]);
	let currentSkip = $state(0);
	let hasMore = $state(false);
	let loading = $state(false);

	async function fetchRoomMessages() {
		pageLoading = true;
		try {
			const [messages, countData] = await Promise.all([
				getRoomMessages(data.roomId, { skip: 0, limit: data.limit }),
				getMessagesCount({ room_id: data.roomId }).catch(() => ({ total: 0 }))
			]);
			const total = countData.total ?? 0;
			data = {
				...data,
				messages,
				total,
				hasMore: messages.length === data.limit,
				_loading: false
			};
			allMessages = [...messages];
			currentSkip = messages.length;
			hasMore = total > data.limit;
		} catch (e) {
			console.error('Room detail fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	let lastFetchKey = null;
	$effect(() => {
		const key = data.roomId;
		if (key === lastFetchKey) return;
		lastFetchKey = key;
		fetchRoomMessages();
	});

	async function loadMore() {
		if (loading || !hasMore) return;
		loading = true;
		try {
			const params = new URLSearchParams();
			params.set('skip', String(currentSkip));
			params.set('limit', String(data.limit));

			const res = await fetch(`/api/v1/rooms/${encodeURIComponent(data.roomId)}/messages?${params.toString()}`);
			if (!res.ok) throw new Error(`API ${res.status}`);
			const newMessages = await res.json();

			allMessages = [...allMessages, ...newMessages];
			currentSkip += newMessages.length;
			hasMore = newMessages.length >= data.limit;
		} catch (e) {
			console.error('Load more error:', e);
			hasMore = false;
		} finally {
			loading = false;
		}
	}
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
	<div class="flex justify-between items-center mb-6">
		<p class="text-sm opacity-60">
			{$t('rooms.messageCount', { count: data.total.toLocaleString() })}
		</p>
		<p class="text-sm opacity-60">
			{allMessages.length} / {data.total}
		</p>
	</div>

	{#if data.error}
		<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
	{/if}

	{#if allMessages.length === 0 && !loading}
		<p class="opacity-60">{$t('messages.noMessages')}</p>
	{:else}
		<div class="space-y-1">
			{#each allMessages as msg}
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

		<InfiniteScroll {loading} {hasMore} onLoadMore={loadMore} />
	{/if}
{/if}