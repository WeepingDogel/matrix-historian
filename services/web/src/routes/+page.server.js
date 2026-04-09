export async function load() {
	return {
		messageCount: 0,
		roomCount: 0,
		userCount: 0,
		recentMessages: [],
		rooms: [],
		users: [],
		overview: null,
		_loading: true
	};
}
