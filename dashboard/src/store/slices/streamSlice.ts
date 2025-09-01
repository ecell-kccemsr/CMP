import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";
import type { StreamMetadata } from "../../types";

interface StreamState {
  streams: StreamMetadata[];
  activeStream: StreamMetadata | null;
  loading: boolean;
  error: string | null;
}

const initialState: StreamState = {
  streams: [],
  activeStream: null,
  loading: false,
  error: null,
};

export const fetchStreams = createAsyncThunk(
  "streams/fetchStreams",
  async () => {
    const response = await axios.get("/api/streams");
    return response.data;
  }
);

const streamSlice = createSlice({
  name: "streams",
  initialState,
  reducers: {
    setActiveStream: (state, action) => {
      state.activeStream = action.payload;
    },
    updateStreamStatus: (state, action) => {
      const { streamId, status, viewerCount, quality } = action.payload;
      const stream = state.streams.find((s) => s.id === streamId);
      if (stream) {
        stream.stream_status = status;
        if (viewerCount !== undefined) stream.viewer_count = viewerCount;
        if (quality) stream.stream_quality = quality;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchStreams.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStreams.fulfilled, (state, action) => {
        state.loading = false;
        state.streams = action.payload;
      })
      .addCase(fetchStreams.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch streams";
      });
  },
});

export const { setActiveStream, updateStreamStatus } = streamSlice.actions;
export default streamSlice.reducer;
