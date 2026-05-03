# MessageService - Labora Backend

A high-performance, real-time messaging microservice for the Labora platform. This service enables secure, bidirectional communication between clients and freelancers within job conversations using WebSocket and REST APIs.

## 🚀 Overview

MessageService is a Django-based microservice that provides:
- **Real-time messaging** via WebSocket with Redis backend
- **REST API** for retrieving chat history
- **JWT authentication** with RS256 algorithm
- **Role-based access control** (Client, Freelancer, Admin)
- **Database persistence** for message storage and retrieval
- **Docker containerization** for easy deployment

## 📋 Features

### Core Messaging
- ✅ Real-time bidirectional chat over WebSocket
- ✅ Persistent message storage with indexing
- ✅ Chat history retrieval via REST API
- ✅ Message read status tracking
- ✅ Soft deletion support (is_deleted flag)
- ✅ Job-scoped message threads

### Security & Authentication
- 🔒 JWT authentication (RS256)
- 🔒 Role-based permission system (Client, Freelancer, Admin)
- 🔒 User validation for chat access
- 🔒 Secure WebSocket authentication via query parameters
- 🔒 CORS support for cross-origin requests

### Performance & Scalability
- ⚡ Redis-backed channel layer for WebSocket scaling
- ⚡ Database indexes on frequently queried fields
- ⚡ Async/await for non-blocking operations
- ⚡ Connection pooling and resource management

## 📦 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 5.1+ |
| API | Django REST Framework | 3.15+ |
| WebSocket | Django Channels | 4.2+ |
| WebSocket Server | Daphne | 4.2+ |
| HTTP Server | Gunicorn | 23.0+ |
| Authentication | PyJWT | 2.9+ |
| Cache/Message Queue | Redis | 4.2+ (channels-redis) |
| Database | SQLite (dev) / MySQL (prod) | - |
| CORS | django-cors-headers | 4.6+ |

## 🛠 Installation

### Prerequisites
- Python 3.13+
- Redis server running
- JWT public key file (`public.pem`)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Labora-Backend/MessageService_labora.git
   cd MessageService_labora
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create from template
   ```
   
   Required environment variables:
   ```bash
   # Django Settings
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=False
   
   # JWT Configuration
   JWT_PUBLIC_KEY_PATH=/path/to/public.pem
   JWT_ISSUER=your-issuer  # Optional
   JWT_AUDIENCE=your-audience  # Optional
   
   # Redis Configuration
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   
   # Database (if using MySQL)
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=message_service_db
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   
   Or with Daphne for WebSocket support:
   ```bash
   daphne -b 0.0.0.0 -p 8000 project.asgi:application
   ```

## 🐳 Docker Deployment

### Build Docker Image
```bash
# Build from repository root
docker build -f MessageService/Dockerfile -t labora/message-service:latest .
```

### Run Container
```bash
docker run -d \
  --name message-service \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY=your-secret-key \
  -e REDIS_HOST=redis-service \
  -e REDIS_PORT=6379 \
  -e JWT_PUBLIC_KEY_PATH=/app/jwt_keys/public.pem \
  -v /path/to/jwt_keys:/app/jwt_keys:ro \
  labora/message-service:latest
```

### Docker Compose Example
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  message-service:
    build:
      context: .
      dockerfile: MessageService/Dockerfile
    ports:
      - "8000:8000"
    environment:
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}
      DEBUG: "False"
      REDIS_HOST: redis
      REDIS_PORT: 6379
      JWT_PUBLIC_KEY_PATH: /app/jwt_keys/public.pem
    volumes:
      - ./jwt_keys:/app/jwt_keys:ro
    depends_on:
      - redis
```

## 📡 API Endpoints

### REST API

#### 1. Get Chat History
**Endpoint:** `GET /api/messages/chat-history/`

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
```
job_id (required): Integer - The job ID for which to fetch messages
```

**Example Request:**
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/messages/chat-history/?job_id=123"
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "sender_id": 101,
    "receiver_id": 102,
    "job_id": 123,
    "content": "Hello, are you interested in this job?",
    "is_read": true,
    "is_deleted": false,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "sender_id": 102,
    "receiver_id": 101,
    "job_id": 123,
    "content": "Yes, I'm interested!",
    "is_read": false,
    "is_deleted": false,
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

### WebSocket API

#### 1. Connect to Chat Room
**WebSocket URL:** `ws://localhost:8000/ws/chat/{job_id}/?token=<JWT_TOKEN>`

**Parameters:**
- `job_id`: Integer - The job ID for the chat room
- `token`: JWT token passed as query parameter

**Example JavaScript Client:**
```javascript
const token = "your-jwt-token";
const jobId = 123;
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/${jobId}/?token=${token}`
);

ws.onopen = () => {
  console.log("Connected to chat room");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received message:", message);
  // {
  //   "type": "chat_message",
  //   "id": 1,
  //   "sender_id": 101,
  //   "receiver_id": 102,
  //   "content": "Hello!",
  //   "created_at": "2024-01-15T10:30:00Z"
  // }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected from chat room");
};

// Send a message
ws.send(JSON.stringify({
  content: "Hello, how are you?",
  receiver_id: 102
}));
```

**Message Format (Send):**
```json
{
  "content": "Message text here",
  "receiver_id": 102
}
```

**Message Format (Receive):**
```json
{
  "type": "chat_message",
  "id": 1,
  "sender_id": 101,
  "receiver_id": 102,
  "content": "Message text here",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## 🗄️ Database Schema

### Message Model

```python
class Message(models.Model):
    sender_id: BigIntegerField      # ID of the user sending the message
    receiver_id: BigIntegerField    # ID of the user receiving the message
    job_id: BigIntegerField         # ID of the associated job
    
    content: TextField              # Message content
    
    is_read: BooleanField          # Message read status (default: False)
    is_deleted: BooleanField       # Soft deletion flag (default: False)
    
    created_at: DateTimeField      # Message creation timestamp
    
    # Indexes for optimized queries
    - Index on (job_id)
    - Index on (receiver_id, is_read)
    - Index on (sender_id, receiver_id)
```

**Table Name:** `messages`

## 🔐 Authentication

The service uses JWT (JSON Web Token) with RS256 algorithm for authentication.

### Token Structure
```json
{
  "user_id": 101,
  "role": "client",
  "iss": "your-issuer",
  "aud": "your-audience",
  "exp": 1642345600
}
```

### Required Claims
- `user_id`: Integer - The authenticated user's ID
- `role`: String - User role (client, freelancer, admin)

### JWT Configuration
Set these environment variables:
```bash
JWT_PUBLIC_KEY_PATH=/path/to/public.pem
JWT_ISSUER=your-issuer  # Optional
JWT_AUDIENCE=your-audience  # Optional
```

## 👥 Role-Based Access Control

The service enforces role-based permissions:

| Role | Permissions |
|------|-------------|
| **Client** | Send/receive messages in their jobs |
| **Freelancer** | Send/receive messages in accepted jobs |
| **Admin** | Full access to all messages |

## 📊 Project Structure

```
MessageService_labora/
├── message/                      # Main application
│   ├── migrations/              # Database migrations
│   ├── __init__.py
│   ├── admin.py                 # Django admin configuration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Message model
│   ├── views.py                 # REST API views
│   ├── serializers.py           # DRF serializers
│   ├── consumers.py             # WebSocket consumers
│   ├── routing.py               # WebSocket routing
│   ├── authentication.py        # JWT authentication
│   ├── permissions.py           # Role-based permissions
│   ├── middleware.py            # JWT WebSocket middleware
│   ├── tests.py                 # Unit tests
│   └── urls.py                  # API URL routing
├── project/                     # Django project settings
│   ├── __init__.py
│   ├── asgi.py                  # ASGI configuration (WebSocket)
│   ├── wsgi.py                  # WSGI configuration (HTTP)
│   ├── settings.py              # Django settings
│   └── urls.py                  # Main URL routing
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

## 🔄 Message Flow

### Sending a Message (WebSocket)
1. Client connects to WebSocket: `ws://host/ws/chat/{job_id}/?token={jwt}`
2. Middleware authenticates JWT token
3. Consumer validates user has access to this job
4. Client sends message: `{"content": "...", "receiver_id": ...}`
5. Message is saved to database
6. Message is broadcast to all connected clients in the chat room
7. All clients receive the message via WebSocket

### Retrieving Chat History (REST API)
1. Client makes GET request with JWT token
2. Server validates JWT authentication
3. Server verifies user role (Client/Freelancer/Admin)
4. Server filters messages for the job where user is sender or receiver
5. Messages are returned ordered by creation time

## 🧪 Testing

### Run Unit Tests
```bash
python manage.py test message
```

### Run Specific Test Class
```bash
python manage.py test message.tests.TestMessageModel
```

### Run with Verbose Output
```bash
python manage.py test message -v 2
```

## 🐛 Troubleshooting

### Issue: WebSocket Connection Refused
**Solution:** Ensure Redis is running and Daphne is serving the ASGI application:
```bash
# Check Redis
redis-cli ping  # Should respond with PONG

# Use Daphne instead of runserver
daphne -b 0.0.0.0 -p 8000 project.asgi:application
```

### Issue: JWT Authentication Failed
**Solution:** Verify JWT configuration:
```bash
# Check public key exists and is readable
cat $JWT_PUBLIC_KEY_PATH

# Verify JWT claims in token
python -c "import jwt; print(jwt.decode(token, options={'verify_signature': False}))"
```

### Issue: Messages Not Persisting
**Solution:** Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Redis Connection Error
**Solution:** Check Redis connection parameters:
```bash
# Test Redis connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# Check Channels Redis configuration in settings.py
```

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Configure secure `DJANGO_SECRET_KEY`
- [ ] Set up SSL/TLS for WebSocket (WSS)
- [ ] Configure production database (MySQL/PostgreSQL)
- [ ] Set up Redis with persistence
- [ ] Mount JWT public key file securely
- [ ] Configure appropriate CORS origins
- [ ] Set up logging and monitoring
- [ ] Configure database backups
- [ ] Test authentication and authorization

## 📝 Environment Variables

### Required
- `JWT_PUBLIC_KEY_PATH`: Path to JWT public key PEM file

### Recommended
- `DJANGO_SECRET_KEY`: Django secret key (min 50 chars)
- `DEBUG`: Set to "False" for production
- `REDIS_HOST`: Redis server hostname (default: 127.0.0.1)
- `REDIS_PORT`: Redis server port (default: 6379)

### Optional
- `JWT_ISSUER`: Expected JWT issuer
- `JWT_AUDIENCE`: Expected JWT audience
- `DB_ENGINE`: Database engine (default: sqlite3)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## 📄 License

This project is part of the Labora Backend platform. All rights reserved.

## 📧 Support

For issues, questions, or suggestions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Contact the development team

---

**Last Updated:** May 2024  
**Version:** 1.0.0  
**Maintained by:** Labora Backend Team
