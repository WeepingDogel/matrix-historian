export async function load({ url }) {
	return {
		messages: [],
		total: 0,
		hasMore: false,
		nextSkip: null,
		query: url.searchParams.get('q') || '',
		skip: 0,
		limit: 50,
		room_id: url.searchParams.get('room_id') || '',
		user_id: url.searchParams.get('user_id') || '',
		start_date: url.searchParams.get('start_date') || '',
		end_date: url.searchParams.get('end_date') || '',
		sort: url.searchParams.get('sort') || 'desc',
		_loading: true
	};
}
