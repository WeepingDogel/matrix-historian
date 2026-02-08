import { getMessagesCount, getRooms, getUsers, getMessages, getAnalyticsOverview } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const [countData, rooms, users, recent, overview] = await Promise.all([
			getMessagesCount({}, fetch),
			getRooms({ limit: 100 }, fetch),
			getUsers({ limit: 100 }, fetch),
			getMessages({ limit: 10 }, fetch),
			getAnalyticsOverview(fetch).catch(() => null)
		]);

		return {
			messageCount: countData.total ?? 0,
			roomCount: rooms.length ?? 0,
			userCount: users.length ?? 0,
			recentMessages: recent.messages ?? [],
			rooms: rooms.slice(0, 5),
			users: users.slice(0, 5),
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
