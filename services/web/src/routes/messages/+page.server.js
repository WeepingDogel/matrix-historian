/** @type {import('./$types').PageLoad} */
export async function load({ url, fetch }) {
    const skip = parseInt(url.searchParams.get('skip') || '0');
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const q = url.searchParams.get('q') || '';
    const roomId = url.searchParams.get('room_id') || '';
    const userId = url.searchParams.get('user_id') || '';
    const startDate = url.searchParams.get('start_date') || '';
    const endDate = url.searchParams.get('end_date') || '';
    const sort = url.searchParams.get('sort') || 'desc';

    let messages = [];
    let total = 0;
    let hasMore = false;
    let nextSkip = null;

    if (q) {
        // Search results - no cache for real-time search
        const params = new URLSearchParams({ query: q, sort });
        if (roomId) params.set('room_id', roomId);
        if (userId) params.set('user_id', userId);
        if (startDate) params.set('after', startDate);
        if (endDate) params.set('before', endDate);
        
        const res = await fetch(`/api/v1/search/?${params.toString()}`);
        const data = await res.json();
        messages = data.messages || [];
        total = data.total || 0;
    } else {
        // Message list - no server-side cache (data is highly dynamic)
        // But browser may use Cache-Control headers from API
        const params = new URLSearchParams({ sort, limit: String(limit), skip: String(skip) });
        if (roomId) params.set('room_id', roomId);
        if (userId) params.set('user_id', userId);
        if (startDate) params.set('after', startDate);
        if (endDate) params.set('before', endDate);

        const res = await fetch(`/api/v1/messages/?${params.toString()}`);
        const data = await res.json();
        messages = data.messages || [];
        total = data.total || 0;
    }

    hasMore = total > (skip + limit);
    nextSkip = hasMore ? skip + limit : null;

    return {
        messages: messages,
        total: total,
        hasMore: hasMore,
        nextSkip: nextSkip,
        query: q,
        skip: skip,
        limit: limit,
        room_id: roomId,
        user_id: userId,
        start_date: startDate,
        end_date: endDate,
        sort: sort,
        _loading: false
    };
}