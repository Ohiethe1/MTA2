# Registration System Documentation

## Overview

A complete user registration and management system has been added to the MTA Exception Form Application. This system allows users to register new accounts and administrators to manage existing users.

## Features

### 1. User Registration
- **Frontend**: Registration page at `/register`
- **Backend**: POST `/api/register`
- **Features**:
  - Username validation (minimum 3 characters)
  - Password validation (minimum 6 characters)
  - Password confirmation
  - Duplicate username prevention
  - Automatic redirect to login after successful registration

### 2. User Login
- **Frontend**: Login page at `/login`
- **Backend**: POST `/api/login`
- **Features**:
  - Secure password authentication
  - JWT-like token system (currently using dummy tokens)
  - Session management

### 3. User Management
- **Frontend**: User management page at `/users`
- **Backend**: 
  - GET `/api/users` - List all users
  - DELETE `/api/users/<id>` - Delete a user
- **Features**:
  - View all registered users
  - Delete users with confirmation
  - Real-time updates after user deletion

## API Endpoints

### Registration
```http
POST /api/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "message": "Registration successful! You can now login.",
  "user": {
    "id": "newuser",
    "name": "newuser",
    "bscId": "newuser",
    "role": "user"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing username/password or validation failed
- `409 Conflict`: Username already exists

### Login
```http
POST /api/login
Content-Type: application/json

{
  "username": "existinguser",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful!",
  "token": "dummy-token-123",
  "user": {
    "id": "existinguser",
    "name": "existinguser",
    "bscId": "existinguser",
    "role": "user"
  }
}
```

**Error Response:**
- `401 Unauthorized`: Invalid credentials

### User Management

#### Get All Users
```http
GET /api/users
```

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "user1"
    },
    {
      "id": 2,
      "username": "user2"
    }
  ]
}
```

#### Delete User
```http
DELETE /api/users/1
```

**Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

**Error Response:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Database error

## Frontend Components

### Register Component (`/src/components/Register.tsx`)
- Form with username, password, and confirm password fields
- Client-side validation
- Loading states
- Error handling
- Automatic redirect to login after successful registration

### Login Component (`/src/components/Login.tsx`)
- Updated with link to registration page
- Existing login functionality maintained

### UserManagement Component (`/src/components/UserManagement.tsx`)
- Table displaying all users
- Delete functionality with confirmation
- Real-time updates
- Loading states and error handling

## Navigation

### Header Updates
- Added "Users" link in the main navigation
- Accessible at `/users` for authenticated users

### Routing
- `/register` - Registration page (public)
- `/login` - Login page (public)
- `/users` - User management page (protected)

## Security Features

1. **Password Hashing**: All passwords are hashed using `pbkdf2:sha256`
2. **Input Validation**: Both client-side and server-side validation
3. **Protected Routes**: User management requires authentication
4. **Duplicate Prevention**: Username uniqueness enforced at database level

## Database Schema

The system uses the existing `users.db` SQLite database with the following schema:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

## Testing

A comprehensive test script (`test_registration_system.py`) is included that tests:
- User registration
- User login
- User listing
- Duplicate registration prevention

Run the tests with:
```bash
python3 test_registration_system.py
```

## Usage Instructions

### For New Users
1. Navigate to `/register`
2. Enter username (minimum 3 characters)
3. Enter password (minimum 6 characters)
4. Confirm password
5. Click "Register"
6. You'll be redirected to login page
7. Login with your credentials

### For Administrators
1. Login to the system
2. Navigate to `/users` in the header
3. View all registered users
4. Delete users as needed (with confirmation)

## Future Enhancements

1. **Role-based Access Control**: Add admin roles for user management
2. **Password Reset**: Implement password reset functionality
3. **Email Verification**: Add email verification for new registrations
4. **User Profiles**: Allow users to update their information
5. **Activity Logging**: Track user registration and management activities

## Technical Notes

- The system integrates seamlessly with the existing authentication context
- All new components follow the existing design patterns
- Backend endpoints follow RESTful conventions
- Frontend uses React Router for navigation
- Tailwind CSS is used for styling consistency 