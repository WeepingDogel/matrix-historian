/**
 * Catch-all proxy: forwards /api/* requests to the backend API service.
 * This ensures client-side fetch('/api/v1/...') works in production
 * where there is no Vite dev proxy.
 */
const API_URL = process.env.API_URL || 'http://localhost:8000';

async function proxy({ request, params }) {
	const target = `${API_URL}/api/${params.path}`;
	const url = new URL(target);

	// Forward query string
	const incoming = new URL(request.url);
	url.search = incoming.search;

	const res = await fetch(url.toString(), {
		method: request.method,
		headers: request.headers,
		body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
		duplex: 'half'
	});

	return new Response(res.body, {
		status: res.status,
		statusText: res.statusText,
		headers: res.headers
	});
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
