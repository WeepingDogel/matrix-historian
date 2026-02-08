import { getRoomMessages, getMessagesCount } from '$lib/api.js';

export async function load({ fetch, params, url }) {
	const skip = parseInt(url.searchParams.get('skip') || '0', 10);
	const limit = 100;

	try {
		const [messages, countData] = await Promise.all([
			getRoomMessages(params.id, { skip, limit }, fetch),
			getMessagesCount({ room_id: params.id }, fetch).catch(() => ({ total: 0 }))
		]);

		return {
			roomId: params.id,
			messages,
			total: countData.total ?? 0,
			skip,
			limit,
			hasMore: messages.length === limit
		};
	} catch (e) {
		console.error('Room detail load error:', e);
		return { roomId: params.id, messages: [], total: 0, skip, limit, hasMore: false, error: e.message };
	}
}
