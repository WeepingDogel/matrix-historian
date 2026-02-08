import {
	getMessageStats, getUserActivity, getRoomActivity,
	getAnalyticsOverview, getWordcloud, getActivityHeatmap,
	getTrends, getInteractions, getMessagesCount, getRooms, getUsers
} from '$lib/api.js';

export async function load({ fetch, url }) {
	const interval = url.searchParams.get('interval') || 'day';

	try {
		const [msgStats, userActivity, roomActivity, overview, wordcloud, heatmap, trends, interactions, countData, rooms, users] = await Promise.all([
			getMessageStats(14, fetch).catch(() => ({ stats: [] })),
			getUserActivity(10, fetch).catch(() => ({ users: [] })),
			getRoomActivity(10, fetch).catch(() => ({ rooms: [] })),
			getAnalyticsOverview(fetch).catch(() => null),
			getWordcloud(fetch).catch(() => ({ messages: [] })),
			getActivityHeatmap(fetch).catch(() => ({ heatmap: [], weekdays: [], hours: [] })),
			getTrends(interval, fetch).catch(() => ({ trends: [] })),
			getInteractions(fetch).catch(() => ({ interactions: [] })),
			getMessagesCount({}, fetch).catch(() => ({ total: 0 })),
			getRooms({ limit: 1000 }, fetch).catch(() => []),
			getUsers({ limit: 1000 }, fetch).catch(() => [])
		]);

		// Compute totals from count endpoint and list lengths
		const totalMessages = countData.total ?? 0;
		const totalRooms = Array.isArray(rooms) ? rooms.length : 0;
		const totalUsers = Array.isArray(users) ? users.length : 0;

		// Compute avg messages per day from message stats
		const stats = msgStats.stats ?? [];
		const avgPerDay = stats.length > 0
			? Math.round(stats.reduce((sum, s) => sum + (s.count ?? s[1] ?? 0), 0) / stats.length)
			: 0;

		// Extract hourly activity from overview if available
		const hourlyActivity = overview?.hourly_activity ?? [];

		return {
			messageStats: stats,
			userActivity: userActivity.users ?? [],
			roomActivity: roomActivity.rooms ?? [],
			totalMessages,
			totalRooms,
			totalUsers,
			avgPerDay,
			hourlyActivity,
			wordcloud: wordcloud.messages ?? wordcloud.words ?? [],
			heatmap: heatmap.heatmap ?? [],
			heatmapWeekdays: heatmap.weekdays ?? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
			heatmapHours: heatmap.hours ?? Array.from({ length: 24 }, (_, i) => i),
			trends: trends.trends ?? [],
			interval,
			interactions: interactions.interactions ?? []
		};
	} catch (e) {
		console.error('Analytics load error:', e);
		return {
			messageStats: [], userActivity: [], roomActivity: [],
			totalMessages: 0, totalRooms: 0, totalUsers: 0, avgPerDay: 0,
			hourlyActivity: [],
			wordcloud: [], heatmap: [],
			heatmapWeekdays: [], heatmapHours: [],
			trends: [], interval, interactions: [],
			error: e.message
		};
	}
}
