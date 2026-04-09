export async function load({ url }) {
	return {
		media: [],
		total: 0,
		hasMore: false,
		nextSkip: null,
		skip: 0,
		limit: 48,
		mimeFilter: url.searchParams.get('type') || '',
		stats: null,
		_loading: true
	};
}
