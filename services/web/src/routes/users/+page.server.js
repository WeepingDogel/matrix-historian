import { getUsers, searchUsers, getUserActivity } from '$lib/api.js';

export async function load({ fetch, url }) {
	const q = url.searchParams.get('q') || '';

	try {
		const [users, activity] = await Promise.all([
			q ? searchUsers(q, { limit: 200 }, fetch) : getUsers({ limit: 200 }, fetch),
			getUserActivity(200, fetch).catch(() => ({ users: [] }))
		]);

		// Build a lookup of user_id -> message_count
		const activityMap = {};
		for (const u of activity.users ?? []) {
			const id = u.user_id || u.user;
			if (id) activityMap[id] = u.message_count ?? 0;
		}

		return { users, activityMap, query: q };
	} catch (e) {
		console.error('Users load error:', e);
		return { users: [], activityMap: {}, query: q, error: e.message };
	}
}
