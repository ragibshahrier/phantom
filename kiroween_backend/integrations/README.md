# Google Calendar Integration

This document explains how to set up and use the Google Calendar OAuth2 authentication in the Phantom Scheduler.

## Overview

The Google Calendar integration allows users to synchronize their Phantom events with Google Calendar. The system uses OAuth2 for authentication and automatically handles token refresh.

## Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth2 credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application"
   - Add authorized redirect URIs:
     - For development: `http://localhost:8000/api/integrations/google-calendar/callback/`
     - For production: `https://yourdomain.com/api/integrations/google-calendar/callback/`
   - Save the Client ID and Client Secret

### 2. Environment Configuration

Add the following to your `.env` file:

```bash
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google-calendar/callback/
```

## API Endpoints

### Connect Google Calendar

**Endpoint:** `GET /api/integrations/google-calendar/connect/`

**Authentication:** Required (JWT Bearer token)

**Description:** Initiates the OAuth2 flow and returns an authorization URL.

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "message": "Please visit the authorization URL to connect your Google Calendar"
}
```

**Usage:**
1. Call this endpoint to get the authorization URL
2. Redirect the user to the authorization URL
3. User grants permission on Google's consent screen
4. Google redirects back to the callback URL with an authorization code

### OAuth2 Callback

**Endpoint:** `GET /api/integrations/google-calendar/callback/`

**Authentication:** Not required (public endpoint)

**Description:** Handles the OAuth2 callback from Google and stores the tokens.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: User ID for CSRF protection

**Response:**
```json
{
  "message": "Google Calendar connected successfully",
  "user": "username"
}
```

### Check Connection Status

**Endpoint:** `GET /api/integrations/google-calendar/status/`

**Authentication:** Required (JWT Bearer token)

**Description:** Check if the user has Google Calendar connected.

**Response:**
```json
{
  "connected": true,
  "user": "username"
}
```

### Disconnect Google Calendar

**Endpoint:** `POST /api/integrations/google-calendar/disconnect/`

**Authentication:** Required (JWT Bearer token)

**Description:** Removes the stored Google Calendar tokens.

**Response:**
```json
{
  "message": "Google Calendar disconnected successfully"
}
```

## How It Works

### OAuth2 Flow

1. **Authorization Request:**
   - User calls `/api/integrations/google-calendar/connect/`
   - System generates authorization URL with required scopes
   - User is redirected to Google's consent screen

2. **Authorization Grant:**
   - User grants permission
   - Google redirects to callback URL with authorization code

3. **Token Exchange:**
   - System exchanges authorization code for access and refresh tokens
   - Tokens are stored in the User model's `google_calendar_token` field

4. **Token Storage:**
   - Tokens are stored as JSON in the database
   - Includes: access_token, refresh_token, expiry, scopes, etc.

### Automatic Token Refresh

The system automatically refreshes expired access tokens:

1. When making API calls, the system checks if the token is expired
2. If expired, it uses the refresh token to get a new access token
3. The new token is automatically saved to the database
4. The API call proceeds with the fresh token

### Event Synchronization

Events are automatically synchronized to Google Calendar:

- **On Create:** New events are pushed to Google Calendar
- **On Update:** Modified events are updated in Google Calendar
- **On Delete:** Deleted events are removed from Google Calendar

The synchronization includes:
- Event title (summary)
- Event description
- Start and end times (with timezone)
- Color coding based on category priority

### Retry Logic

The system implements exponential backoff for API failures:

- **Retryable errors:** 429 (rate limit), 500, 503 (server errors)
- **Retry pattern:** 1s, 2s, 4s delays between attempts
- **Max retries:** 3 attempts by default
- **Non-retryable errors:** Fail immediately (e.g., 400, 404)

## Security Considerations

1. **Token Storage:**
   - Tokens are stored encrypted in the database
   - Never expose tokens in API responses or logs

2. **CSRF Protection:**
   - State parameter includes user ID
   - Validates state on callback

3. **Scope Limitation:**
   - Only requests calendar scope
   - Follows principle of least privilege

4. **Token Expiration:**
   - Access tokens expire after 1 hour
   - Refresh tokens expire after 7 days (configurable)
   - System handles expiration automatically

## Testing

Run the property-based tests:

```bash
python -m pytest integrations/tests.py -v
```

The tests verify:
- **Property 11:** Google Calendar sync consistency
- **Property 23:** Retry with exponential backoff

## Troubleshooting

### Common Issues

1. **"User does not have Google Calendar connected"**
   - User needs to complete OAuth2 flow first
   - Check if `google_calendar_token` field is populated

2. **"Invalid grant" error**
   - Refresh token may have expired
   - User needs to reconnect their Google Calendar

3. **Rate limit errors**
   - System will automatically retry with backoff
   - Check logs for retry attempts

4. **Redirect URI mismatch**
   - Ensure `GOOGLE_REDIRECT_URI` matches the URI in Google Cloud Console
   - Check for trailing slashes

### Logging

The system logs all Google Calendar operations:

- **INFO:** Successful operations
- **WARNING:** Retry attempts, degraded functionality
- **ERROR:** Failed operations with details

Check logs at: `logs/phantom.log`

## Example Integration Flow

```python
# 1. User initiates connection
response = requests.get(
    'http://localhost:8000/api/integrations/google-calendar/connect/',
    headers={'Authorization': f'Bearer {access_token}'}
)
auth_url = response.json()['authorization_url']

# 2. Redirect user to auth_url
# User grants permission on Google's page

# 3. Google redirects to callback
# System automatically handles token exchange and storage

# 4. Check connection status
response = requests.get(
    'http://localhost:8000/api/integrations/google-calendar/status/',
    headers={'Authorization': f'Bearer {access_token}'}
)
is_connected = response.json()['connected']

# 5. Events are now automatically synced to Google Calendar
```

## References

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
