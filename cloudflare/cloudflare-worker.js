// Cloudflare Worker script to route /blog to your Django application

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

/**
 * Route requests to the bike blog application
 * @param {Request} request
 */
async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Check if the request is for /blog or a subpath
  if (url.pathname === '/blog' || url.pathname.startsWith('/blog/')) {
    // Forward to your application server (assuming it's hosted elsewhere)
    // Replace YOUR_APP_SERVER_URL with your actual Django application URL
    return fetch(`YOUR_APP_SERVER_URL${url.pathname}${url.search}`, request)
  }
  
  // For other requests, pass through to the origin
  return fetch(request)
}
