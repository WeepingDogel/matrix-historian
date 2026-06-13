<script>
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import InfiniteScroll from '$lib/InfiniteScroll.svelte';
	import { getUserMessages, getMessagesCount } from '$lib/api.js';

	let { data } = $props();
	let pageLoading = $state(true);

	let displayName = $derived(
		data.messages.length > 0
			? (data.messages[0].sender?.display_name || data.userId)
			: data.userId
	);

	// Accumulated messages for infinite scroll
	let allMessages = $state([]);
	let currentSkip = $state(0);
	let hasMore = $state(false);
	let loading = $state(false);

	async function fetchUserMessages() {
		pageLoading = true;
		try {
			const [messages, countData] = await Promise.all([
				getUserMessages(data.userId, { skip: 0, limit: data.limit }),
				getMessagesCount({ user_id: data.userId }).catch(() => ({ total: 0 }))
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
			console.error('User detail fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	let lastFetchKey = null;
	$effect(() => {
		const key = data.userId;
		if (key === lastFetchKey) return;
		lastFetchKey = key;
		fetchUserMessages();
	});

	async function loadMore() {
		if (loading || !hasMore) return;
		loading = true;
		try {
			const params = new URLSearchParams();
			params.set('skip', String(currentSkip));
			params.set('limit', String(data.limit));

			const res = await fetch(`/api/v1/users/${encodeURIComponent(data.userId)}/messages?${params.toString()}`);
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
	<title>{displayName} – {$t('app.title')}</title>
</svelte:head>

<div class="breadcrumbs text-sm mb-4">
	<ul>
		<li><a href="/users">{$t('users.title')}</a></li>
		<li>{displayName}</li>
	</ul>
</div>

<h2 class="text-2xl font-bold mb-2">{displayName}</h2>
<p class="text-xs font-mono opacity-50 mb-2">{data.userId}</p>

{#if pageLoading}
	<div class="space-y-3">
		<Skeleton variant="chat" count={5} />
	</div>
{:else}
	<div class="flex justify-between items-center mb-6">
		<p class="text-sm opacity-60">
			{$t('users.messageCount', { count: data.total.toLocaleString() })}
		</p>
		<p class="text-sm opacity-60">
			{allMessages.length} / {data.total}
		</p>
	</div>

	{#if data.error}
		<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
	{/if}

	{#if allMessages.length === 0 && !loading}
		<p class="opacity-60">{$t('users.noMessagesFrom')}</p>
	{:else}
		<div class="space-y-1">
			{#each allMessages as msg}
				<div class="chat chat-start">
					<div class="chat-header">
						<span class="font-medium">{displayName}</span>
						<time class="text-xs opacity-50 ml-2">
							<Time timestamp={msg.timestamp} />
						</time>
					</div>
					<div class="chat-bubble chat-bubble-secondary">{msg.content}</div>
					<div class="chat-footer opacity-50">
						<a href="/rooms/{encodeURIComponent(msg.room_id)}" class="link link-hover text-xs">
							{msg.room?.name || msg.room_id}
						</a>
					</div>
				</div>
			{/each}
		</div>

		<InfiniteScroll {loading} {hasMore} onLoadMore={loadMore} />
	{/if}
{/if}