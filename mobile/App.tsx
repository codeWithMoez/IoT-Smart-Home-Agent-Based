/**
 * App Entry Point
 * Configures React Query and renders the main dashboard.
 */
import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardScreen from "./src/screens/DashboardScreen";

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
