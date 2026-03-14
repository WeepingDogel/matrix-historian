import { getMessagesCount, getRooms, getUsers, getMessages, getAnalyticsOverview } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const [countData, rooms, users, allRooms, allUsers, recent, overview] = await Promise.all([
			getMessagesCount({}, fetch),
			getRooms({ limit: 5 }, fetch),          // Top 5 for display
			getUsers({ limit: 5 }, fetch),           // Top 5 for display
			getRooms({ limit: 100000 }, fetch),      // All rooms for accurate count
			getUsers({ limit: 100000 }, fetch),      // All users for accurate count
			getMessages({ limit: 10 }, fetch),
			getAnalyticsOverview(fetch).catch(() => null)
		]);

		return {
			messageCount: countData.total ?? 0,
			roomCount: Array.isArray(allRooms) ? allRooms.length : 0,
			userCount: Array.isArray(allUsers) ? allUsers.length : 0,
			recentMessages: recent.messages ?? [],
			rooms: Array.isArray(rooms) ? rooms.slice(0, 5) : [],
			users: Array.isArray(users) ? users.slice(0, 5) : [],
			overview
		};
	} catch (e) {
		console.error('Dashboard load error:', e);
		return {
			messageCount: 0,
			roomCount: 0,
			userCount: 0,
			recentMessages: [],
			rooms: [],
			users: [],
			overview: null,
			error: e.message
		};
	}
}
