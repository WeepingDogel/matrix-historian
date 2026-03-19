import {
	getRooms,
	getRoomsCount,
	searchRooms,
	getSearchRoomsCount,
	getRoomActivity
} from '$lib/api.js';

export async function load({ fetch, url }) {
	const q = url.searchParams.get('q') || '';
	const page = Math.max(1, parseInt(url.searchParams.get('page') || '1', 10));
	const limit = 50;
	const skip = (page - 1) * limit;

	try {
		const [rooms, countResult, activity] = await Promise.all([
			q
				? searchRooms(q, { skip, limit }, fetch)
				: getRooms({ skip, limit }, fetch),
			q
				? getSearchRoomsCount(q, fetch)
				: getRoomsCount(fetch),
			getRoomActivity(200, fetch).catch(() => ({ rooms: [] }))
		]);

		const total = countResult.total ?? 0;

		// Build a lookup of room_id -> message_count from activity data
		const activityMap = {};
		for (const r of activity.rooms ?? []) {
			const id = r.room_id || r.room;
			if (id) activityMap[id] = r.message_count ?? 0;
		}

		return {
			rooms,
			activityMap,
			total,
			skip,
			limit,
			query: q,
			hasMore: total > skip + limit,
			nextSkip: skip + limit
		};
	} catch (e) {
		console.error('Rooms load error:', e);
		return {
			rooms: [],
			activityMap: {},
			total: 0,
			skip,
			limit,
			query: q,
			hasMore: false,
			nextSkip: null,
			error: e.message
		};
	}
}
