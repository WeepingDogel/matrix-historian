import { getRooms } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const rooms = await getRooms({ limit: 200 }, fetch);
		return { rooms };
	} catch (e) {
		console.error('Rooms load error:', e);
		return { rooms: [], error: e.message };
	}
}
