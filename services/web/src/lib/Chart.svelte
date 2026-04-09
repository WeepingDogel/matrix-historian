<script>
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';

	let { type = 'bar', labels = [], datasets = [], options = {} } = $props();

	let container;
	let chart;
	let echarts;
	let resizeObserver;

	function toEChartsOption() {
		const isHorizontal = options.indexAxis === 'y';
		const categoryAxis = {
			type: 'category',
			data: [...labels],
			axisLabel: {
				color: 'rgba(255,255,255,0.6)',
				fontSize: 11,
				rotate: options.scales?.x?.ticks?.maxRotation ?? 0
			},
			axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
			splitLine: { show: false }
		};
		const valueAxis = {
			type: 'value',
			axisLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 11 },
			axisLine: { show: false },
			splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
		};

		const series = datasets.map((ds) => {
			const chartType = type === 'doughnut' ? 'pie' : type;
			const s = { name: ds.label || '', type: chartType, data: [...(ds.data || [])] };

			if (chartType === 'line') {
				s.smooth = ds.tension ? true : false;
				s.lineStyle = { color: ds.borderColor || ds.backgroundColor };
				s.itemStyle = { color: ds.borderColor || ds.backgroundColor };
				if (ds.fill) {
					s.areaStyle = { color: ds.backgroundColor || 'rgba(102,26,230,0.15)' };
				}
				s.symbol = 'circle';
				s.symbolSize = 4;
			} else if (chartType === 'bar') {
				s.itemStyle = {
					color: ds.backgroundColor || '#661ae6',
					borderRadius: ds.borderRadius || 0
				};
				s.barMaxWidth = 40;
			} else if (chartType === 'pie') {
				s.data = labels.map((label, i) => ({
					name: label,
					value: ds.data[i] || 0
				}));
				if (type === 'doughnut') {
					s.radius = ['40%', '70%'];
				} else {
					s.radius = ['0%', '70%'];
				}
				s.label = { color: 'rgba(255,255,255,0.8)' };
			}

			return s;
		});

		const isPie = type === 'pie' || type === 'doughnut';

		const opt = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: isPie ? 'item' : 'axis',
				backgroundColor: 'rgba(30,30,30,0.9)',
				borderColor: 'rgba(255,255,255,0.1)',
				textStyle: { color: '#fff', fontSize: 12 }
			},
			legend: {
				show: datasets.length > 1,
				textStyle: { color: 'rgba(255,255,255,0.6)' },
				top: 0
			},
			grid: isPie ? undefined : {
				left: '3%',
				right: '4%',
				bottom: '3%',
				top: datasets.length > 1 ? 30 : 10,
				containLabel: true
			},
			series
		};

		if (!isPie) {
			if (isHorizontal) {
				opt.yAxis = categoryAxis;
				opt.xAxis = valueAxis;
			} else {
				opt.xAxis = categoryAxis;
				opt.yAxis = valueAxis;
			}
		}

		return opt;
	}

	onMount(async () => {
		const mod = await import('echarts');
		echarts = mod;

		if (container) {
			chart = echarts.init(container, null, { renderer: 'canvas' });
			chart.setOption(toEChartsOption());

			resizeObserver = new ResizeObserver(() => {
				chart?.resize();
			});
			resizeObserver.observe(container);
		}
	});

	onDestroy(() => {
		resizeObserver?.disconnect();
		chart?.dispose();
		chart = null;
	});

	$effect(() => {
		// Track reactive dependencies
		void labels;
		void datasets;
		void options;
		void type;
		if (chart && echarts) {
			chart.setOption(toEChartsOption(), true);
		}
	});
</script>

<div class="w-full" style="min-height: 16rem; position: relative;">
	{#if browser}
		<div bind:this={container} style="width: 100%; height: 100%; min-height: 16rem;"></div>
	{:else}
		<div class="flex items-center justify-center h-64 opacity-40">Loading chart...</div>
	{/if}
</div>
