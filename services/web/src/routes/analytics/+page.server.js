import { getMessageStats, getUserActivity, getRoomActivity } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const [msgStats, userActivity, roomActivity] = await Promise.all([
			getMessageStats(14, fetch),
			getUserActivity(10, fetch),
			getRoomActivity(10, fetch)
		]);

		return {
			messageStats: msgStats.stats ?? [],
			userActivity: userActivity.users ?? [],
			roomActivity: roomActivity.rooms ?? []
		};
	} catch (e) {
		console.error('Analytics load error:', e);
		return {
			messageStats: [],
			userActivity: [],
			roomActivity: [],
			error: e.message
		};
	}
}
