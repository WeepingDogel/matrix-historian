import { getUserMessages } from '$lib/api.js';

export async function load({ fetch, params, url }) {
	const skip = parseInt(url.searchParams.get('skip') || '0', 10);
	const limit = 100;

	try {
		const messages = await getUserMessages(params.id, { skip, limit }, fetch);
		return {
			userId: params.id,
			messages,
			skip,
			hasMore: messages.length === limit
		};
	} catch (e) {
		console.error('User detail load error:', e);
		return { userId: params.id, messages: [], skip, hasMore: false, error: e.message };
	}
}
