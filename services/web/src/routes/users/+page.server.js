import {
	getUsers,
	getUsersCount,
	searchUsers,
	getSearchUsersCount,
	getUserActivity
} from '$lib/api.js';

export async function load({ fetch, url }) {
	const q = url.searchParams.get('q') || '';
	const page = Math.max(1, parseInt(url.searchParams.get('page') || '1', 10));
	const limit = 50;
	const skip = (page - 1) * limit;

	try {
		const [users, countResult, activity] = await Promise.all([
			q
				? searchUsers(q, { skip, limit }, fetch)
				: getUsers({ skip, limit }, fetch),
			q
				? getSearchUsersCount(q, fetch)
				: getUsersCount(fetch),
			getUserActivity(200, fetch).catch(() => ({ users: [] }))
		]);

		const total = countResult.total ?? 0;

		// Build a lookup of user_id -> message_count
		const activityMap = {};
		for (const u of activity.users ?? []) {
			const id = u.user_id || u.user;
			if (id) activityMap[id] = u.message_count ?? 0;
		}

		return {
			users,
			activityMap,
			total,
			skip,
			limit,
			query: q,
			hasMore: total > skip + limit,
			nextSkip: skip + limit
		};
	} catch (e) {
		console.error('Users load error:', e);
		return {
			users: [],
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
