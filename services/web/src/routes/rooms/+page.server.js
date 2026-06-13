export async function load({ url }) {
	return {
		rooms: [],
		activityMap: {},
		total: 0,
		skip: 0,
		limit: 50,
		query: url.searchParams.get('q') || '',
		hasMore: false,
		nextSkip: null,
		_loading: true
	};
}
