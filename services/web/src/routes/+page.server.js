import { getMessagesCount, getRooms, getUsers, getMessages } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const [countData, rooms, users, recent] = await Promise.all([
			getMessagesCount({}, fetch),
			getRooms({ limit: 100 }, fetch),
			getUsers({ limit: 100 }, fetch),
			getMessages({ limit: 10 }, fetch)
		]);

		return {
			messageCount: countData.total ?? 0,
			roomCount: rooms.length ?? 0,
			userCount: users.length ?? 0,
			recentMessages: recent.messages ?? []
		};
	} catch (e) {
		console.error('Dashboard load error:', e);
		return {
			messageCount: 0,
			roomCount: 0,
			userCount: 0,
			recentMessages: [],
			error: e.message
		};
	}
}
