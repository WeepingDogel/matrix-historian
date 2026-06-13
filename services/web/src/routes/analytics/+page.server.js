export async function load({ url }) {
	return {
		messageStats: [],
		userActivity: [],
		roomActivity: [],
		totalMessages: 0,
		totalRooms: 0,
		totalUsers: 0,
		avgPerDay: 0,
		hourlyActivity: [],
		wordcloud: [],
		heatmap: [],
		heatmapWeekdays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
		heatmapHours: Array.from({ length: 24 }, (_, i) => i),
		trends: [],
		interval: url.searchParams.get('interval') || 'day',
		days: parseInt(url.searchParams.get('days') || '7', 10),
		room_id: url.searchParams.get('room_id') || null,
		rooms: [],
		interactions: [],
		userHourlyActivity: { users: [], hours: [], days: 7, user_count: 0 },
		sentiment: null,
		userNetwork: null,
		topicEvolution: null,
		messageSummary: null,
		_loading: true
	};
}
