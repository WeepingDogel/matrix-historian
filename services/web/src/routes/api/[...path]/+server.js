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

	// Follow redirects (FastAPI may 307 for trailing slash normalization)
	const res = await fetch(url.toString(), {
		method: request.method,
		headers: request.headers,
		body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
		duplex: 'half',
		redirect: 'follow'
	});

	// Strip redirect-related headers before forwarding back
	const responseHeaders = new Headers(res.headers);
	responseHeaders.delete('location');

	return new Response(res.body, {
		status: res.status,
		statusText: res.statusText,
		headers: responseHeaders
	});
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
