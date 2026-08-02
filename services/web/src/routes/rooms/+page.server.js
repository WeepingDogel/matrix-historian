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
        console.error("Failed to load rooms:", e);
    }

    return { rooms };
}
