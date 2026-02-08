import { getMessages, searchMessages } from '$lib/api.js';

export async function load({ fetch, url }) {
	const q = url.searchParams.get('q') || '';
	const skip = parseInt(url.searchParams.get('skip') || '0', 10);
	const limit = 50;

	try {
		let result;
		if (q) {
			result = await searchMessages(q, { skip, limit }, fetch);
		} else {
			result = await getMessages({ skip, limit }, fetch);
		}
		return {
			messages: result.messages ?? [],
			total: result.total ?? 0,
			hasMore: result.has_more ?? false,
			nextSkip: result.next_skip,
			query: q,
			skip
		};
	} catch (e) {
		console.error('Messages load error:', e);
		return { messages: [], total: 0, hasMore: false, nextSkip: null, query: q, skip, error: e.message };
	}
}
