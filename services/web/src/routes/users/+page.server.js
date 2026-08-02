/** @type {import('./$types').PageLoad} */
export async function load({ url, fetch }) {
    const skip = parseInt(url.searchParams.get('skip') || '0');
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const q = url.searchParams.get('q') || '';

    let users = [];
    let total = 0;
    let hasMore = false;
    let nextSkip = null;

    if (q) {
        // Search results - no cache for real-time search
        const res = await fetch(`/api/v1/users/search/?query=${encodeURIComponent(q)}&skip=${skip}&limit=${limit}`);
        const data = await res.json();
        users = data || [];
        // Get search count
        const countRes = await fetch(`/api/v1/users/search/count?query=${encodeURIComponent(q)}`);
        const countData = await countRes.json();
        total = countData.total || 0;
    } else {
        // List users - use medium cache (3 min)
        const res = await fetch(`/api/v1/users/?skip=${skip}&limit=${limit}`, { next: { ttl: 180000 } });
        users = await res.json();

        // Get total count - use longer cache (5 min)
        const countRes = await fetch('/api/v1/users/count', { next: { ttl: 300000 } });
        const countData = await countRes.json();
        total = countData.total || 0;
    }

    hasMore = total > (skip + limit);
    nextSkip = hasMore ? skip + limit : null;

    return {
        users: users || [],
        activityMap: {},
        total: total,
        skip: skip,
        limit: limit,
        query: q,
        hasMore: hasMore,
        nextSkip: nextSkip,
        _loading: false
    };
}
