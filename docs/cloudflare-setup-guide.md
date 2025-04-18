# Cloudflare Setup Guide for Your Bicycle Blog

This guide will walk you through setting up your Django bicycle blog on Cloudflare, specifically at the URL path `vista-grande.net/blog`.

## Option 1: Using Cloudflare Pages for Full Hosting

If you want to host your Django application completely on Cloudflare:

### Step 1: Install Cloudflare Pages Functions

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```

2. Log in to your Cloudflare account:
   ```bash
   wrangler login
   ```

### Step 2: Create a Pages Project

1. Initialize a new Pages project:
   ```bash
   wrangler pages project create bicycle-blog
   ```

2. Create a `functions` directory in your project root:
   ```bash
   mkdir -p functions/blog
   ```

3. Create a Python adapter file at `functions/blog/[[path]].py`:
   ```python
   from bicycle_blog.wsgi import application

   def on_request(request, env, ctx):
       # Handle the request using Django's WSGI application
       # This is simplified; actual implementation needs Python WSGI adapter
       return application(request, env)
   ```

4. Deploy your project:
   ```bash
   wrangler pages deploy
   ```

5. In the Cloudflare dashboard, go to Pages > your project > Settings > Custom domains and add `vista-grande.net`.

## Option 2: Using a Worker with a Backend (Recommended)

This option assumes you're hosting your Django application on a traditional server or cloud service.

### Step 1: Set Up Your Django Application on a Hosting Provider

1. Deploy your Django application to a hosting provider like DigitalOcean, AWS, etc.
2. Make sure it's accessible via a URL, e.g., `blog-app.example.com`

### Step 2: Create a Cloudflare Worker

1. Log in to your Cloudflare dashboard
2. Go to Workers & Pages > Create a Worker
3. Use the Cloudflare Worker script provided in this project
4. Replace `YOUR_APP_SERVER_URL` with your actual backend URL

### Step 3: Configure Worker Routes

1. After creating your worker, go to Workers & Pages > your worker > Triggers
2. Add a route pattern: `vista-grande.net/blog*`
3. This will route all requests to `/blog` and its sub-paths to your worker

### Step 4: Configure DNS

1. Make sure your domain `vista-grande.net` is added to Cloudflare
2. Verify DNS settings are correct in the DNS tab

## Option 3: Using Cloudflare Tunnels (For Private Networks)

If your Django application is hosted on a private network:

### Step 1: Install cloudflared

```bash
# On Debian/Ubuntu
apt install cloudflared

# On macOS
brew install cloudflare/cloudflare/cloudflared
```

### Step 2: Authenticate cloudflared

```bash
cloudflared tunnel login
```

### Step 3: Create a Tunnel

```bash
cloudflared tunnel create bicycle-blog
```

### Step 4: Configure the Tunnel

Create a configuration file `config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /path/to/credentials.json

ingress:
  - hostname: vista-grande.net
    path: /blog
    service: http://localhost:8000
  - service: http_status:404
```

### Step 5: Start the Tunnel

```bash
cloudflared tunnel run bicycle-blog
```

### Step 6: Configure DNS

```bash
cloudflared tunnel route dns bicycle-blog vista-grande.net
```

## Setting Up for Your Specific Case

Based on your requirements, Option 2 (Using a Worker with a Backend) is likely the most straightforward approach:

1. Host your Django application on a traditional web server
2. Set up a Cloudflare Worker to route `/blog` requests to your application
3. Configure your Django application to work with the `/blog` base path

## Important Configuration Notes

1. **Django Settings**: Make sure your Django application is configured with:
   - `FORCE_SCRIPT_NAME = '/blog'`
   - Correctly configured static and media URLs

2. **CORS Settings**: If you're using a separate domain for your backend, ensure CORS is properly configured.

3. **Security**: Set up proper SSL configurations and ensure your backend is secured.

4. **Caching**: Cloudflare provides excellent caching capabilities. Configure your Django application to take advantage of this by setting appropriate cache headers.
