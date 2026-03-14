<script>
	/**
	 * Animated number counter component
	 * Smoothly counts up from 0 to the target value on mount/change
	 */
	let { value = 0, duration = 1200, formatFn } = $props();

	let displayed = $state(0);
	let animFrame = null;

	function format(n) {
		if (formatFn) return formatFn(n);
		return Math.round(n).toLocaleString();
	}

	$effect(() => {
		const target = Number(value) || 0;
		const start = displayed;
		const diff = target - start;
		if (diff === 0) return;

		const startTime = performance.now();

		function tick(now) {
			const elapsed = now - startTime;
			const progress = Math.min(elapsed / duration, 1);
			// ease-out cubic
			const eased = 1 - Math.pow(1 - progress, 3);
			displayed = start + diff * eased;

			if (progress < 1) {
				animFrame = requestAnimationFrame(tick);
			} else {
				displayed = target;
			}
		}

		if (animFrame) cancelAnimationFrame(animFrame);
		animFrame = requestAnimationFrame(tick);

		return () => {
			if (animFrame) cancelAnimationFrame(animFrame);
		};
	});
</script>

{format(displayed)}
