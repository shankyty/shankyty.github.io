# Authenticating a WebSocket connection

Authenticating a WebSocket connection is a critical step and works differently from standard, stateless HTTP requests. Since the user has already signed in, we have an existing authenticated session, which we need to securely associate with the long-lived WebSocket connection.

The core principle is that authentication happens once, during the initial HTTP handshake that "upgrades" the connection to a WebSocket. Once the connection is established, it is considered authenticated for its entire lifecycle on the server side.

Here are the two most common and effective methods to achieve this:

Method 1: Token-Based Authentication (JWT - Recommended)

This is the modern, stateless approach, ideal for distributed systems and microservices. The flow works as follows:

Step 1: User Signs In & Receives a Token

The user signs in using a standard HTTP POST request with their credentials (e.g., username/password).

The server validates the credentials and generates a JSON Web Token (JWT). This token contains a payload with user information (like userId, username) and an expiration time (exp).

The server signs the token with a secret key and sends it back to the client.

Step 2: Client Initiates WebSocket Connection with the Token
The client now needs to send this JWT to the server during the WebSocket handshake. There are a few ways to do this:

(Recommended) As a Query Parameter: The client initiates the connection to an endpoint like:
wss://chat.example.com/socket?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
This is simple and widely supported.

As a Cookie: When the user logs in, the JWT can be stored in a secure cookie. The browser will automatically include this cookie in the WebSocket handshake request because it's just an HTTP GET request initially.

Using the Sec-WebSocket-Protocol Header: The client can send the token as a subprotocol. This is less common but viable. For example: 
Sec-WebSocket-Protocol: jwt, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Step 3: Server Validates the Token During Handshake

The chat server receives the HTTP GET request with the Upgrade: websocket header.

It extracts the JWT from the query parameter (or cookie/header).

The server then validates the token:

Verifies the signature using its secret key.

Checks the expiration time (exp) to ensure it's not expired.

Validates any other claims (like issuer iss or audience aud).

If the token is valid, the server associates the connection with the userId from the token's payload. It then sends back an HTTP 101 Switching Protocols response. The connection is now upgraded and authenticated.

If the token is invalid, the server rejects the handshake with a standard HTTP error code like 401 Unauthorized or 403 Forbidden.

Method 2: Session Cookie-Based Authentication (Traditional)

This is a stateful approach, common in monolithic applications where the web server and WebSocket server share a session store (like Redis).

Step 1: User Signs In

The user logs in via a standard HTTP POST request.

The server creates a session, stores the user's ID in it, and saves the session data in a central session store (e.g., Redis).

The server sends a unique session_id back to the client in a secure, HttpOnly cookie.

Step 2: Client Initiates WebSocket Connection

The client's browser automatically attaches the session_id cookie to the WebSocket handshake request, as it's going to the same domain.

The client simply tries to connect to wss://chat.example.com/socket.

Step 3: Server Validates the Session

The chat server receives the handshake request and extracts the session_id from the cookie.

It queries the central session store (Redis) with this ID.

If a valid, active session is found for a user, the server associates the connection with that userId.

The server completes the handshake (HTTP 101). If the session is invalid or expired, it rejects the connection (401/403).

Lifecycle and Security Considerations After Connection

Once the connection is established, you need to manage its lifecycle:

Token Expiration: A JWT is typically short-lived (e.g., 15-60 minutes). What happens if it expires while the WebSocket is still open?

Server-Side Check: The server should store the token's expiration time when the connection is established. It can gracefully terminate the connection when the token expires, forcing the client to reconnect with a new token.

Client-Side Refresh: A better user experience is for the server to send a custom "re-authenticate" message just before expiration. The client then uses a separate refresh token (obtained at login) to get a new JWT via a standard HTTP request and then sends this new token over the existing WebSocket to re-authenticate the connection without dropping it.

Forced Logout: If the user logs out from another browser tab, the WebSocket connection should be terminated. This requires a Pub/Sub mechanism (like Redis Pub/Sub). The HTTP logout endpoint publishes a user-logged-out event with the userId. The WebSocket server subscribes to this channel and, upon receiving an event, forcefully closes the connection for that userId.

Always Use WSS: The wss:// protocol (WebSocket over TLS) is non-negotiable. It encrypts the entire connection, including the initial handshake, preventing tokens or session IDs from being intercepted in a man-in-the-middle attack.

In summary, you leverage the initial HTTP upgrade request to pass a credential—either a self-contained JWT or a session cookie—which the server validates before establishing the secure, long-lived WebSocket connection.