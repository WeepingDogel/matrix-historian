<script>
	import { onMount, onDestroy } from 'svelte';
	import {
		Chart as ChartJS,
		CategoryScale,
		LinearScale,
		BarElement,
		LineElement,
		PointElement,
		ArcElement,
		Filler,
		Tooltip,
		Legend
	} from 'chart.js';

	ChartJS.register(
		CategoryScale,
		LinearScale,
		BarElement,
		LineElement,
		PointElement,
		ArcElement,
		Filler,
		Tooltip,
		Legend
	);

	let { type = 'bar', labels = [], datasets = [], options = {} } = $props();

	let canvas;
	let chart;

	function buildConfig() {
		return {
			type,
			data: { labels, datasets },
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

	onMount(() => {
		chart = new ChartJS(canvas, buildConfig());
	});

	onDestroy(() => {
		chart?.destroy();
	});

	// Reactively update chart when data changes
	$effect(() => {
		if (chart) {
			chart.data.labels = labels;
			chart.data.datasets = datasets;
			chart.options = { ...chart.options, ...options };
			chart.update();
		}
	});
</script>

<div class="w-full h-64">
	<canvas bind:this={canvas}></canvas>
</div>
