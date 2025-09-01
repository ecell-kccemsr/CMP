-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create classrooms table
CREATE TABLE classrooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_id INTEGER REFERENCES users(id),
    rtmp_key VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE
);

-- Create stream_metadata table
CREATE TABLE stream_metadata (
    id SERIAL PRIMARY KEY,
    classroom_id INTEGER REFERENCES classrooms(id),
    stream_start TIMESTAMP WITH TIME ZONE,
    stream_end TIMESTAMP WITH TIME ZONE,
    stream_quality JSON,
    viewer_count INTEGER DEFAULT 0,
    stream_status VARCHAR(20),
    hls_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better query performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_classrooms_teacher ON classrooms(teacher_id);
CREATE INDEX idx_stream_metadata_classroom ON stream_metadata(classroom_id);
CREATE INDEX idx_classrooms_status ON classrooms(status);
