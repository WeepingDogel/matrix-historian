<script>
	import { t } from '$lib/i18n';
	import { formatTime } from '$lib/timezone';
	import Time from '$lib/Time.svelte';
	import Skeleton from '$lib/Skeleton.svelte';
	import { getUserMessages, getMessagesCount } from '$lib/api.js';

	let { data } = $props();
	let pageLoading = $state(true);

	let displayName = $derived(
		data.messages.length > 0
			? (data.messages[0].sender?.display_name || data.userId)
			: data.userId
	);

	let currentPage = $derived(Math.floor(data.skip / data.limit) + 1);
	let totalPages = $derived(Math.ceil(data.total / data.limit) || 1);

	async function fetchUserMessages() {
		pageLoading = true;
		try {
			const [messages, countData] = await Promise.all([
				getUserMessages(data.userId, { skip: data.skip, limit: data.limit }),
				getMessagesCount({ user_id: data.userId }).catch(() => ({ total: 0 }))
			]);
			data = {
				...data,
				messages,
				total: countData.total ?? 0,
				hasMore: messages.length === data.limit,
				_loading: false
			};
		} catch (e) {
			console.error('User detail fetch error:', e);
		} finally {
			pageLoading = false;
		}
	}

	$effect(() => {
		void data.userId;
		void data.skip;
		fetchUserMessages();
	});
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
	<p class="text-sm opacity-60 mb-6">
		{$t('users.messageCount', { count: data.total.toLocaleString() })}
		{#if data.total > 0}· {$t('common.page')} {currentPage} {$t('common.of')} {totalPages}{/if}
	</p>

	{#if data.error}
		<div class="alert alert-warning mb-4"><span>{$t('common.error', { error: data.error })}</span></div>
	{/if}

	{#if data.messages.length === 0}
		<p class="opacity-60">{$t('users.noMessagesFrom')}</p>
	{:else}
		<div class="space-y-1">
			{#each data.messages as msg}
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

		<div class="flex items-center gap-2 mt-6 justify-center">
			{#if data.skip > 0}
				<a href="/users/{encodeURIComponent(data.userId)}?skip={Math.max(0, data.skip - data.limit)}" class="btn btn-outline btn-sm">
					{$t('common.previous')}
				</a>
			{/if}
			<span class="text-sm opacity-60">{$t('common.page')} {currentPage} {$t('common.of')} {totalPages}</span>
			{#if data.hasMore}
				<a href="/users/{encodeURIComponent(data.userId)}?skip={data.skip + data.limit}" class="btn btn-outline btn-sm">
					{$t('common.next')}
				</a>
			{/if}
		</div>
	{/if}
{/if}
