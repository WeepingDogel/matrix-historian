import {
	getMessageStats, getUserActivity, getRoomActivity,
	getAnalyticsOverview, getWordcloud, getActivityHeatmap,
	getTrends, getInteractions, getContentAnalysis, getUserNetwork
} from '$lib/api.js';

export async function load({ fetch, url }) {
	const interval = url.searchParams.get('interval') || 'day';

	try {
		const [msgStats, userActivity, roomActivity, overview, wordcloud, heatmap, trends, interactions, contentAnalysis, userNetwork] = await Promise.all([
			getMessageStats(14, fetch).catch(() => ({ stats: [] })),
			getUserActivity(10, fetch).catch(() => ({ users: [] })),
			getRoomActivity(10, fetch).catch(() => ({ rooms: [] })),
			getAnalyticsOverview(fetch).catch(() => null),
			getWordcloud(fetch).catch(() => ({ messages: [] })),
			getActivityHeatmap(fetch).catch(() => ({ heatmap: [], weekdays: [], hours: [] })),
			getTrends(interval, fetch).catch(() => ({ trends: [] })),
			getInteractions(fetch).catch(() => ({ interactions: [] })),
			getContentAnalysis(fetch).catch(() => ({ words: [] })),
			getUserNetwork(fetch).catch(() => ({ nodes: [], edges: [] }))
		]);

		return {
			messageStats: msgStats.stats ?? [],
			userActivity: userActivity.users ?? [],
			roomActivity: roomActivity.rooms ?? [],
			overview,
			wordcloud: wordcloud.messages ?? wordcloud.words ?? [],
			heatmap: heatmap.heatmap ?? [],
			heatmapWeekdays: heatmap.weekdays ?? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
			heatmapHours: heatmap.hours ?? Array.from({ length: 24 }, (_, i) => i),
			trends: trends.trends ?? [],
			interval,
			interactions: interactions.interactions ?? [],
			contentAnalysis: contentAnalysis.words ?? [],
			userNetwork
		};
	} catch (e) {
		console.error('Analytics load error:', e);
		return {
			messageStats: [], userActivity: [], roomActivity: [],
			overview: null, wordcloud: [], heatmap: [],
			heatmapWeekdays: [], heatmapHours: [],
			trends: [], interval, interactions: [],
			contentAnalysis: [], userNetwork: null,
			error: e.message
		};
	}
}
