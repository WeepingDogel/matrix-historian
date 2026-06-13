export async function load({ params, url }) {
	return {
		roomId: params.id,
		messages: [],
		total: 0,
		skip: parseInt(url.searchParams.get('skip') || '0', 10),
		limit: 100,
		hasMore: false,
		_loading: true
	};
}
