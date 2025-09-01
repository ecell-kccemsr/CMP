import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";
import type { Classroom } from "../../types";

interface ClassroomState {
  classrooms: Classroom[];
  loading: boolean;
  error: string | null;
}

const initialState: ClassroomState = {
  classrooms: [],
  loading: false,
  error: null,
};

export const fetchClassrooms = createAsyncThunk(
  "classrooms/fetchClassrooms",
  async () => {
    const response = await axios.get("/api/classrooms");
    return response.data;
  }
);

export const createClassroom = createAsyncThunk(
  "classrooms/createClassroom",
  async (name: string) => {
    const response = await axios.post("/api/classrooms", { name });
    return response.data;
  }
);

const classroomSlice = createSlice({
  name: "classrooms",
  initialState,
  reducers: {
    updateClassroomStatus: (state, action) => {
      const { id, status } = action.payload;
      const classroom = state.classrooms.find((c) => c.id === id);
      if (classroom) {
        classroom.status = status;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchClassrooms.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchClassrooms.fulfilled, (state, action) => {
        state.loading = false;
        state.classrooms = action.payload;
      })
      .addCase(fetchClassrooms.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch classrooms";
      })
      .addCase(createClassroom.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createClassroom.fulfilled, (state, action) => {
        state.loading = false;
        state.classrooms.push(action.payload);
      })
      .addCase(createClassroom.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to create classroom";
      });
  },
});

export const { updateClassroomStatus } = classroomSlice.actions;
export default classroomSlice.reducer;
