export async function load({ url, fetch }) {
    const interval = url.searchParams.get('interval') || 'day';
    const days = parseInt(url.searchParams.get('days') || '7', 10);
    const roomId = url.searchParams.get('room_id') || null;

    // Build params for API calls
    const baseParams = new URLSearchParams({ interval, days });
    if (roomId) baseParams.set('room_id', roomId);

    // Use longer cache for analytics (15 min) since data is aggregated
    const overviewRes = await fetch(`/api/v1/analytics/overview?${baseParams.toString()}`, { next: { ttl: 900000 } });
    const overview = await overviewRes.json();

    // Hourly activity - moderate cache (10 min)
    const hourlyParams = new URLSearchParams({ interval: 'hour', days: String(days) });
    if (roomId) hourlyParams.set('room_id', roomId);
    const hourlyRes = await fetch(`/api/v1/analytics/hourly?${hourlyParams.toString()}`, { next: { ttl: 600000 } });
    const hourlyActivity = await hourlyRes.json();

    // Top rooms - longer cache (15 min)
    const topRoomsRes = await fetch('/api/v1/analytics/top-rooms?limit=20&days=' + days, { next: { ttl: 900000 } });
    const topRooms = await topRoomsRes.json();

    // Top users - longer cache (15 min)
    const topUsersRes = await fetch('/api/v1/analytics/top-users?limit=20&days=' + days, { next: { ttl: 900000 } });
    const topUsers = await topUsersRes.json();

    // Trends - moderate cache (10 min)
    const trendsRes = await fetch(`/api/v1/analytics/trends?${baseParams.toString()}`, { next: { ttl: 600000 } });
    const trends = await trendsRes.json();

    return {
        messageStats: overview?.message_stats || [],
        userActivity: overview?.user_activity || [],
        roomActivity: overview?.room_activity || [],
        totalMessages: overview?.total_messages || 0,
        totalRooms: overview?.total_rooms || 0,
        totalUsers: overview?.total_users || 0,
        avgPerDay: overview?.avg_per_day || 0,
        hourlyActivity: hourlyActivity?.data || [],
        wordcloud: [],  // Not yet implemented in API
        heatmap: [],    // Not yet implemented in API
        heatmapWeekdays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        heatmapHours: Array.from({ length: 24 }, (_, i) => i),
        trends: trends?.data || [],
        topRooms: topRooms?.top_rooms || [],
        topUsers: topUsers?.top_users || [],
        interval: interval,
        days: days,
        room_id: roomId,
        rooms: [],
        interactions: [],
        userHourlyActivity: { users: [], hours: [], days: days, user_count: 0 },
        sentiment: null,
        userNetwork: null,
        topicEvolution: null,
        messageSummary: null,
        _loading: false
    };
}


