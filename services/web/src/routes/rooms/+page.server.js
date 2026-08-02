import { base } from "$app/paths";

export async function load({ fetch }) {
    let rooms = [];
    try {
        const response = await fetch(`${base}/api/v1/rooms/?skip=0&limit=50`);
        if (response.ok) {
            const data = await response.json();
            rooms = data.rooms || [];
        }
    } catch (e) {
        console.error('Failed to load rooms:', e);
    }

    return { rooms };
}

</content>
<write_to_file>
<path>services/web/src/routes/users/+page.server.js</path>
<content>
import { base } from "$app/paths";

export async function load({ fetch }) {
    let users = [];
    try {
        const response = await fetch(`${base}/api/v1/users/?skip=0&limit=50`);
        if (response.ok) {
            const data = await response.json();
            users = data.users || [];
        }
    } catch (e) {
        console.error('Failed to load users:', e);
    }

    return { users };
}

</content>
<write_to_file>
<path>services/web/src/routes/messages/+page.server.js</path>
<content>
import { base } from "$app/paths";

export async function load({ fetch }) {
    let messages = [];
    try {
        const response = await fetch(`${base}/api/v1/messages/?skip=0&limit=50`);
        if (response.ok) {
            const data = await response.json();
            messages = data.messages || [];
        }
    } catch (e) {
        console.error('Failed to load messages:', e);
    }

    return { messages };
}

</content>
<write_to_file>
<path>services/web/src/routes/analytics/+page.server.js</path>
<content>
import { base } from "$app/paths";

export async function load({ fetch }) {
    let overview = {};
    let wordcloud = [];
    let trends = [];
    let heatmap = [];

    try {
        const response = await fetch(`${base}/api/v1/analytics/overview`);
        if (response.ok) {
            overview = await response.json();
        }
    } catch (e) {
        console.error('Failed to load analytics overview:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/analytics/wordcloud?limit=50`);
        if (response.ok) {
            const data = await response.json();
            wordcloud = data.messages || [];
        }
    } catch (e) {
        console.error('Failed to load wordcloud:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/analytics/trends?interval=day`);
        if (response.ok) {
            const data = await response.json();
            trends = data.trends || [];
        }
    } catch (e) {
        console.error('Failed to load trends:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/analytics/activity-heatmap`);
        if (response.ok) {
            const data = await response.json();
            heatmap = data.heatmap || [];
        }
    } catch (e) {
        console.error('Failed to load heatmap:', e);
    }

    return { overview, wordcloud, trends, heatmap };
}

</content>
<write_to_file>
<path>services/web/src/routes/rooms/[id]/+page.server.js</path>
<content>
import { base } from "$app/paths";

export async function load({ fetch, params }) {
    let room = null;
    let messages = [];
    let media = [];

    try {
        const response = await fetch(`${base}/api/v1/rooms/${params.id}`);
        if (response.ok) {
            room = await response.json();
        }
    } catch (e) {
        console.error('Failed to load room:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/messages/?room_id=${params.id}&skip=0&limit=50`);
        if (response.ok) {
            const data = await response.json();
            messages = data.messages || [];
        }
    } catch (e) {
        console.error('Failed to load messages:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/media/room/${params.id}?skip=0&limit=20`);
        if (response.ok) {
            const data = await response.json();
            media = data.media || [];
        }
    } catch (e) {
        console.error('Failed to load media:', e);
    }

    return { room, messages, media };
}

</content>
<write_to_file>
<path>services/web/src/routes/users/[id]/+page.server.js</path>
<content>
import { base } from "$app/paths";

export async function load({ fetch, params }) {
    let user = null;
    let messages = [];
    let media = [];

    try {
        const response = await fetch(`${base}/api/v1/users/${params.id}`);
        if (response.ok) {
            user = await response.json();
        }
    } catch (e) {
        console.error('Failed to load user:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/messages/?sender_id=${params.id}&skip=0&limit=50`);
        if (response.ok) {
            const data = await response.json();
            messages = data.messages || [];
        }
    } catch (e) {
        console.error('Failed to load messages:', e);
    }

    try {
        const response = await fetch(`${base}/api/v1/media/user/${params.id}?skip=0&limit=20`);
        if (response.ok) {
            const data = await response.json();
            media = data.media || [];
        }
    } catch (e) {
        console.error('Failed to load media:', e);
    }

    return { user, messages, media };
}