import { getMessages, searchMessages, getMessagesCount, getRooms, getUsers } from '$lib/api.js';

export async function load({ fetch, url }) {
	const q = url.searchParams.get('q') || '';
	const skip = parseInt(url.searchParams.get('skip') || '0', 10);
	const room_id = url.searchParams.get('room_id') || '';
	const user_id = url.searchParams.get('user_id') || '';
	const limit = 50;

	try {
		const [result, rooms, users] = await Promise.all([
			q
				? searchMessages(q, { skip, limit, room_id: room_id || undefined, user_id: user_id || undefined }, fetch)
				: getMessages({ skip, limit, room_id: room_id || undefined, user_id: user_id || undefined }, fetch),
			getRooms({ limit: 200 }, fetch).catch(() => []),
			getUsers({ limit: 200 }, fetch).catch(() => [])
		]);

		return {
			messages: result.messages ?? [],
			total: result.total ?? 0,
			hasMore: result.has_more ?? false,
			nextSkip: result.next_skip,
			query: q,
			skip,
			limit,
			room_id,
			user_id,
			rooms,
			users
		};
	} catch (e) {
		console.error('Messages load error:', e);
		return {
			messages: [], total: 0, hasMore: false, nextSkip: null,
			query: q, skip, limit, room_id, user_id,
			rooms: [], users: [], error: e.message
		};
	}
}
