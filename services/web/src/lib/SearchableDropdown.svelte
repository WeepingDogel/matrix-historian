<script>
	import { t } from '$lib/i18n';

	let {
		value = '',
		placeholder = '',
		searchFn,
		labelKey = 'name',
		valueKey = 'id',
		fallbackLabelKey = '',
		onchange
	} = $props();

	let open = $state(false);
	let searchQuery = $state('');
	let items = $state([]);
	let loading = $state(false);
	let hasMore = $state(true);
	let skip = $state(0);
	let sentinel;
	let dropdownRef;
	let debounceTimer;
	const PAGE_SIZE = 20;

	// Selected item label
	let selectedLabel = $state('');

	function getLabel(item) {
		return item[labelKey] || (fallbackLabelKey ? item[fallbackLabelKey] : '') || item[valueKey] || '';
	}

	async function fetchItems(reset = false) {
		if (loading) return;
		if (reset) {
			skip = 0;
			items = [];
			hasMore = true;
		}
		if (!hasMore && !reset) return;
		loading = true;
		try {
			const result = await searchFn(searchQuery, skip, PAGE_SIZE);
			const newItems = Array.isArray(result) ? result : (result.rooms ?? result.users ?? result.items ?? []);
			if (newItems.length < PAGE_SIZE) hasMore = false;
			items = reset ? newItems : [...items, ...newItems];
			skip = items.length;

			// Update selected label if we find the item
			if (value && !selectedLabel) {
				const found = items.find(item => item[valueKey] === value);
				if (found) selectedLabel = getLabel(found);
			}
		} catch {
			hasMore = false;
		} finally {
			loading = false;
		}
	}

	function onSearchInput(e) {
		searchQuery = e.target.value;
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => fetchItems(true), 300);
	}

	function selectItem(item) {
		const val = item ? item[valueKey] : '';
		selectedLabel = item ? getLabel(item) : '';
		open = false;
		searchQuery = '';
		if (onchange) onchange(val);
	}

	function selectAll() {
		selectedLabel = '';
		open = false;
		searchQuery = '';
		if (onchange) onchange('');
	}

	function toggleOpen() {
		open = !open;
		if (open) {
			fetchItems(true);
		}
	}

	// Close on click outside
	function handleClickOutside(e) {
		if (dropdownRef && !dropdownRef.contains(e.target)) {
			open = false;
		}
	}

	// Intersection observer for infinite scroll in dropdown
	$effect(() => {
		if (!sentinel || !open) return;
		const observer = new IntersectionObserver((entries) => {
			if (entries[0].isIntersecting && hasMore && !loading) {
				fetchItems();
			}
		}, { rootMargin: '100px' });
		observer.observe(sentinel);
		return () => observer.disconnect();
	});

	// Resolve label on mount if value is set
	$effect(() => {
		if (value && !selectedLabel && searchFn) {
			fetchItems(true);
		}
	});
</script>

<svelte:window onclick={handleClickOutside} />

<div class="relative" bind:this={dropdownRef}>
	<button
		type="button"
		class="select select-bordered select-sm w-56 text-left flex items-center"
		onclick={toggleOpen}
	>
		<span class="flex-1 truncate">
			{value && selectedLabel ? selectedLabel : placeholder}
		</span>
		<span class="text-xs opacity-50">{open ? '▲' : '▼'}</span>
	</button>

	{#if open}
		<div class="absolute z-50 mt-1 w-64 bg-base-200 border border-base-300 rounded-box shadow-lg max-h-64 flex flex-col">
			<div class="p-2 border-b border-base-300">
				<input
					type="text"
					class="input input-bordered input-xs w-full"
					placeholder={$t('common.search')}
					value={searchQuery}
					oninput={onSearchInput}
					autofocus
				/>
			</div>
			<div class="overflow-y-auto flex-1">
				<!-- All option -->
				<button
					type="button"
					class="w-full text-left px-3 py-1.5 text-sm hover:bg-base-300 transition-colors {!value ? 'font-bold text-primary' : ''}"
					onclick={selectAll}
				>
					{placeholder}
				</button>

				{#each items as item}
					<button
						type="button"
						class="w-full text-left px-3 py-1.5 text-sm hover:bg-base-300 transition-colors truncate {item[valueKey] === value ? 'font-bold text-primary' : ''}"
						onclick={() => selectItem(item)}
					>
						{getLabel(item)}
					</button>
				{/each}

				{#if loading}
					<div class="px-3 py-2 text-xs opacity-50 text-center">Loading...</div>
				{/if}

				<!-- Sentinel for infinite scroll -->
				<div bind:this={sentinel} class="h-1"></div>
			</div>
		</div>
	{/if}
</div>
