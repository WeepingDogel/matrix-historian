export async function load({ fetch }) {
    // Use SvelteKit's built-in fetch caching with revalidate
    const [messageCountRes, roomCountRes, userCountRes] = await Promise.all([
        fetch('/api/v1/messages/count', { next: { ttl: 300000 } }),   // 5 min cache
        fetch('/api/v1/rooms/count', { next: { ttl: 300000 } }),      // 5 min cache
        fetch('/api/v1/users/count', { next: { ttl: 300000 } })       // 5 min cache
    ]);

    const messageCount = await messageCountRes.json();
    const roomCount = await roomCountRes.json();
    const userCount = await userCountRes.json();

    // Recent messages - shorter cache since data is dynamic
    const recentRes = await fetch('/api/v1/messages/?limit=5&sort=desc', { next: { ttl: 60000 } });  // 1 min
    const recentMessages = await recentRes.json();

    // Rooms list - moderate cache
    const roomsRes = await fetch('/api/v1/rooms/?limit=10&skip=0', { next: { ttl: 180000 } });  // 3 min
    const rooms = await roomsRes.json();

    // Users list - moderate cache
    const usersRes = await fetch('/api/v1/users/?limit=10&skip=0', { next: { ttl: 180000 } });  // 3 min
    const users = await usersRes.json();

    // Overview analytics - longer cache
    const overviewRes = await fetch('/api/v1/analytics/overview?days=7', { next: { ttl: 900000 } });  // 15 min
    const overview = await overviewRes.json();

    return {
        messageCount: messageCount.total || 0,
        roomCount: roomCount.total || 0,
        userCount: userCount.total || 0,
        recentMessages: recentMessages.messages || [],
        rooms: rooms || [],
        users: users || [],
        overview: overview || null,
        _loading: false
    };
}


