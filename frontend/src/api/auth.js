import { apiClient } from "./client";

export async function signup({ email, password, fullName }) {
  const { data } = await apiClient.post("/auth/signup", {
    email,
    password,
    full_name: fullName || null,
  });
  return data;
}

export async function login({ email, password }) {
  const { data } = await apiClient.post("/auth/login", { email, password });
  return data;
}
