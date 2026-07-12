import { apiClient } from "./client";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocuments() {
  const { data } = await apiClient.get("/documents");
  return data;
}
export async function deleteDocument(id) {
  const { data } = await apiClient.delete(`/documents/${id}`);
  return data;
}