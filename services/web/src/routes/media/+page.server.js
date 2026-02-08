import { getMedia } from '$lib/api.js';

export async function load({ fetch, url }) {
	const skip = parseInt(url.searchParams.get('skip') || '0', 10);
	const mimeFilter = url.searchParams.get('type') || '';
	const limit = 48;

	try {
		const result = await getMedia({ skip, limit, mime_type: mimeFilter || undefined }, fetch);
		return {
			media: result.media ?? [],
			total: result.total ?? 0,
			hasMore: result.has_more ?? false,
			nextSkip: result.next_skip,
			skip,
			mimeFilter
		};
	} catch (e) {
		console.error('Media load error:', e);
		return { media: [], total: 0, hasMore: false, nextSkip: null, skip, mimeFilter, error: e.message };
	}
}
