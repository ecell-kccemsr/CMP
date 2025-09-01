import { configureStore } from "@reduxjs/toolkit";
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";
import type { ThunkAction, Action } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import classroomReducer from "./slices/classroomSlice";
import streamReducer from "./slices/streamSlice";
import type { RootState } from "../types";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    classrooms: classroomReducer,
    streams: streamReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ["auth/login/fulfilled", "auth/register/fulfilled"],
        // Ignore these field paths in all actions
        ignoredActionPaths: ["payload.timestamp", "meta.timestamp"],
        // Ignore these paths in the state
        ignoredPaths: ["auth.user", "streams.activeStream"],
      },
    }),
});

export type AppDispatch = typeof store.dispatch;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;

// Use throughout your app instead of plain `useDispatch` and `useSelector`
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
