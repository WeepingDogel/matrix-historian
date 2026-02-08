import { getUsers } from '$lib/api.js';

export async function load({ fetch }) {
	try {
		const users = await getUsers({ limit: 200 }, fetch);
		return { users };
	} catch (e) {
		console.error('Users load error:', e);
		return { users: [], error: e.message };
	}
}
