<script>
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';

	let { type = 'bar', labels = [], datasets = [], options = {} } = $props();

	let canvas;
	let chart;
	let ChartJS;

	onMount(async () => {
		// Dynamic import — Chart.js only loads on the client, never during SSR
		const mod = await import('chart.js');
		ChartJS = mod.Chart;
		ChartJS.register(
			// Controllers (required for each chart type)
			mod.BarController,
			mod.LineController,
			mod.PieController,
			mod.DoughnutController,
			// Scales
			mod.CategoryScale,
			mod.LinearScale,
			// Elements
			mod.BarElement,
			mod.LineElement,
			mod.PointElement,
			mod.ArcElement,
			// Plugins
			mod.Filler,
			mod.Tooltip,
			mod.Legend
		);

		if (canvas) {
			chart = new ChartJS(canvas, buildConfig());
		}
	});

	onDestroy(() => {
		if (chart) {
			chart.destroy();
			chart = null;
		}
	});

	function buildConfig() {
		return {
			type,
			data: {
				labels: [...labels],
				datasets: datasets.map((ds) => ({ ...ds, data: [...(ds.data || [])] }))
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: datasets.length > 1 }
				},
				...options
			}
		};
	}

	// Reactively update chart when props change
	$effect(() => {
		if (chart && ChartJS) {
			chart.data.labels = [...labels];
			chart.data.datasets = datasets.map((ds) => ({ ...ds, data: [...(ds.data || [])] }));
			Object.assign(chart.options, options);
			chart.update('none');
		}
	});
</script>

<div class="w-full" style="min-height: 16rem; position: relative;">
	{#if browser}
		<canvas bind:this={canvas}></canvas>
	{:else}
		<div class="flex items-center justify-center h-64 opacity-40">Loading chart…</div>
	{/if}
</div>
