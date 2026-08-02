import { base } from "$app/paths";

export async function load({ fetch }) {
    let overview = [];
    try {
        const response = await fetch(`${base}/api/v1/analytics/overview`);
        if (response.ok) {
            overview = await response.json();
        }
    } catch (e) {
        console.error('Failed to load overview:', e);
    }

    let users = [];
    try {
        const response = await fetch(`${base}/api/v1/users/?skip=0&limit=10`);
        if (response.ok) {
            const data = await response.json();
            users = data.users || [];
        }
    } catch (e) {
        console.error('Failed to load users:', e);
    }

    let messages = [];
    try {
        const response = await fetch(`${base}/api/v1/messages/?skip=0&limit=10`);
        if (response.ok) {
            const data = await response.json();
            messages = data.messages || [];
        }
    } catch (e) {
        console.error('Failed to load messages:', e);
    }

    let rooms = [];
    try {
        const response = await fetch(`${base}/api/v1/rooms/?skip=0&limit=10`);
        if (response.ok) {
            const data = await response.json();
            rooms = data.rooms || [];
        }
    } catch (e) {
        console.error('Failed to load rooms:', e);
    }

    let media = [];
    try {
        const response = await fetch(`${base}/api/v1/media/?skip=0&limit=10`);
        if (response.ok) {
            const data = await response.json();
            media = data.media || [];
        }
    } catch (e) {
        console.error('Failed to load media:', e);
    }

    return { overview, users, messages, rooms, media };
}
