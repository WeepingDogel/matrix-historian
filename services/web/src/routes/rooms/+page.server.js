import { getRooms, getRoomActivity } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const [rooms, activity] = await Promise.all([
			getRooms({ limit: 200 }, fetch),
			getRoomActivity(200, fetch).catch(() => ({ rooms: [] }))
		]);

		// Build a lookup of room_id -> message_count from activity data
		const activityMap = {};
		for (const r of activity.rooms ?? []) {
			const id = r.room_id || r.room;
			if (id) activityMap[id] = r.message_count ?? 0;
		}

		return { rooms, activityMap };
	} catch (e) {
		console.error('Rooms load error:', e);
		return { rooms: [], activityMap: {}, error: e.message };
	}
}
