/**
 * API client helpers for Matrix Historian web frontend.
 * Each function hits the SvelteKit /api proxy which forwards to the backend.
 */

const BASE = '/api/v1';

/**
 * Tiny wrapper around fetch that throws on non-OK responses.
 */
async function request(path, params = {}, fetchFn = fetch) {
	// Strip trailing slash to avoid SvelteKit 308 redirects (trailingSlash: 'never')
	const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;

	const url = new URL(cleanPath, 'http://localhost'); // URL only used for searchParams
	for (const [k, v] of Object.entries(params)) {
		if (v !== undefined && v !== null && v !== '') {
			url.searchParams.set(k, String(v));
		}
	}
	const qs = url.searchParams.toString();
	const fullPath = qs ? `${cleanPath}?${qs}` : cleanPath;

	const res = await fetchFn(fullPath);
	if (!res.ok) {
		throw new Error(`API ${res.status}: ${res.statusText}`);
	}
	return res.json();
}

// ─── Messages ───────────────────────────────────────────────────────

export function getMessages(opts = {}, fetchFn = fetch) {
	const { skip, limit, room_id, user_id } = opts;
	return request(`${BASE}/messages/`, { skip, limit, room_id, user_id }, fetchFn);
}

export function getMessagesCount(opts = {}, fetchFn = fetch) {
	const { room_id, user_id, query } = opts;
	return request(`${BASE}/messages/count`, { room_id, user_id, query }, fetchFn);
}

export function getMessage(eventId, fetchFn = fetch) {
	return request(`${BASE}/messages/${encodeURIComponent(eventId)}`, {}, fetchFn);
}

export function searchMessages(query, opts = {}, fetchFn = fetch) {
	const { skip, limit, room_id, user_id } = opts;
	return request(`${BASE}/search/`, { query, skip, limit, room_id, user_id }, fetchFn);
}

// ─── Rooms ──────────────────────────────────────────────────────────

export function getRooms(opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/rooms/`, { skip, limit }, fetchFn);
}

export function getRoomMessages(roomId, opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/rooms/${encodeURIComponent(roomId)}/messages`, { skip, limit }, fetchFn);
}

// ─── Users ──────────────────────────────────────────────────────────

export function getUsers(opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/users/`, { skip, limit }, fetchFn);
}

export function getUserMessages(userId, opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/users/${encodeURIComponent(userId)}/messages`, { skip, limit }, fetchFn);
}

export function searchUsers(query, opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/users/search/`, { query, skip, limit }, fetchFn);
}

// ─── Media ──────────────────────────────────────────────────────────

export function getMedia(opts = {}, fetchFn = fetch) {
	const { skip, limit, mime_type } = opts;
	return request(`${BASE}/media/`, { skip, limit, mime_type }, fetchFn);
}

export function getMediaStats(fetchFn = fetch) {
	return request(`${BASE}/media/stats`, {}, fetchFn);
}

export function getMediaByRoom(roomId, opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/media/room/${encodeURIComponent(roomId)}`, { skip, limit }, fetchFn);
}

export function getMediaByUser(userId, opts = {}, fetchFn = fetch) {
	const { skip, limit } = opts;
	return request(`${BASE}/media/user/${encodeURIComponent(userId)}`, { skip, limit }, fetchFn);
}

export function getMediaMetadata(mediaId, fetchFn = fetch) {
	return request(`${BASE}/media/${encodeURIComponent(mediaId)}`, {}, fetchFn);
}

// ─── Analytics ──────────────────────────────────────────────────────

export function getMessageStats(days = 7, fetchFn = fetch) {
	return request(`${BASE}/analytics/message-stats`, { days }, fetchFn);
}

export function getUserActivity(limit = 10, fetchFn = fetch) {
	return request(`${BASE}/analytics/user-activity`, { limit }, fetchFn);
}

export function getRoomActivity(limit = 10, fetchFn = fetch) {
	return request(`${BASE}/analytics/room-activity`, { limit }, fetchFn);
}

export function getAnalyticsOverview(fetchFn = fetch) {
	return request(`${BASE}/analytics/overview`, {}, fetchFn);
}

export function getWordcloud(fetchFn = fetch) {
	return request(`${BASE}/analytics/wordcloud`, {}, fetchFn);
}

export function getInteractions(fetchFn = fetch) {
	return request(`${BASE}/analytics/interactions`, {}, fetchFn);
}

export function getTrends(interval = 'day', fetchFn = fetch) {
	return request(`${BASE}/analytics/trends`, { interval }, fetchFn);
}

export function getActivityHeatmap(fetchFn = fetch) {
	return request(`${BASE}/analytics/activity-heatmap`, {}, fetchFn);
}

export function getSentiment(fetchFn = fetch) {
	return request(`${BASE}/analytics/sentiment`, {}, fetchFn);
}

export function getTopicEvolution(fetchFn = fetch) {
	return request(`${BASE}/analytics/topic-evolution`, {}, fetchFn);
}

export function getAiAnalysis(fetchFn = fetch) {
	return request(`${BASE}/analytics/ai-analysis`, {}, fetchFn);
}

export function getContentAnalysis(fetchFn = fetch) {
	return request(`${BASE}/analytics/content-analysis`, {}, fetchFn);
}

export function getUserNetwork(fetchFn = fetch) {
	return request(`${BASE}/analytics/user-network`, {}, fetchFn);
}

// ─── Health ─────────────────────────────────────────────────────────

export function getHealth(fetchFn = fetch) {
	return request(`${BASE}/health`, {}, fetchFn);
}
