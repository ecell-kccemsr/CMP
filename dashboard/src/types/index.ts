// Import types from '@reduxjs/toolkit' that are used in slices

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface Classroom {
  id: number;
  name: string;
  teacher_id: number;
  rtmp_key: string;
  status: string;
  last_active: string;
}

export interface ClassroomState {
  classrooms: Classroom[];
  loading: boolean;
  error: string | null;
}

export interface StreamMetadata {
  id: number;
  classroom_id: number;
  stream_start: string;
  stream_end: string | null;
  stream_quality: {
    bitrate: number;
    resolution: string;
    fps: number;
  };
  viewer_count: number;
  stream_status: string;
  hls_url: string;
}

export interface StreamState {
  streams: StreamMetadata[];
  activeStream: StreamMetadata | null;
  loading: boolean;
  error: string | null;
}

export interface RootState {
  auth: AuthState;
  classrooms: ClassroomState;
  streams: StreamState;
}
