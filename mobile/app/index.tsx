/**
 * App Root - Entry Point (Expo Router)
 * Note: Using App.tsx at root as main entry point instead.
 */
import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardScreen from "../src/screens/DashboardScreen";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardScreen />
    </QueryClientProvider>
  );
}
