import {
	getMessageStats, getUserActivity, getRoomActivity,
	getAnalyticsOverview, getWordcloud, getActivityHeatmap,
	getTrends, getInteractions, getMessagesCount, getRooms, getUsers,
	getUserHourlyActivity, getSentiment, getContentAnalysis,
	getUserNetwork, getTopicEvolution, getAiAnalysis
} from '$lib/api.js';

export async function load({ fetch, url }) {
	const interval = url.searchParams.get('interval') || 'day';
	const days = parseInt(url.searchParams.get('days') || '7', 10);
	const room_id = url.searchParams.get('room_id') || null;

	try {
		const [msgStats, userActivity, roomActivity, overview, wordcloud, heatmap, trends, interactions, countData, rooms, users, userHourly, sentiment, contentAnalysis, userNetwork, topicEvolution, messageSummary] = await Promise.all([
			getMessageStats(days, fetch).catch(() => ({ stats: [] })),
			getUserActivity(10, fetch).catch(() => ({ users: [] })),
			getRoomActivity(10, fetch).catch(() => ({ rooms: [] })),
			getAnalyticsOverview(fetch).catch(() => null),
			getWordcloud({ days, room_id }, fetch).catch(() => ({ messages: [] })),
			getActivityHeatmap({ days, room_id }, fetch).catch(() => ({ heatmap: [], weekdays: [], hours: [] })),
			getTrends({ interval, days }, fetch).catch(() => ({ trends: [] })),
			getInteractions({ days }, fetch).catch(() => ({ interactions: [] })),
			getMessagesCount({}, fetch).catch(() => ({ total: 0 })),
			getRooms({ limit: 100000 }, fetch).catch(() => []),
			getUsers({ limit: 100000 }, fetch).catch(() => []),
			getUserHourlyActivity({ days, room_id, limit: 10 }, fetch).catch(() => ({ users: [], hours: [], days: 7, user_count: 0 })),
			getSentiment({ days, room_id }, fetch).catch(() => null),
			getContentAnalysis({ days, room_id }, fetch).catch(() => null),
			getUserNetwork({ days, room_id }, fetch).catch(() => null),
			getTopicEvolution({ days, room_id }, fetch).catch(() => null),
			getAiAnalysis({ days, room_id, analysis_type: 'summary' }, fetch).catch(() => null)
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
			days,
			room_id,
			rooms: Array.isArray(rooms) ? rooms : [],
			interactions: interactions.interactions ?? [],
			userHourlyActivity: userHourly,
			sentiment,
			contentAnalysis,
			userNetwork,
			topicEvolution,
			messageSummary
		};
	} catch (e) {
		console.error('Analytics load error:', e);
		return {
			messageStats: [], userActivity: [], roomActivity: [],
			totalMessages: 0, totalRooms: 0, totalUsers: 0, avgPerDay: 0,
			hourlyActivity: [],
			wordcloud: [], heatmap: [],
			heatmapWeekdays: [], heatmapHours: [],
			trends: [], interval, days, room_id,
			rooms: [],
			interactions: [],
			userHourlyActivity: { users: [], hours: [], days: 7, user_count: 0 },
			sentiment: null, contentAnalysis: null, userNetwork: null, topicEvolution: null, messageSummary: null,
			error: e.message
		};
	}
}
