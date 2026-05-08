import request from "@/utils/request";

export function getCategories() {
  return request.get("/categories");
}

export function createCategory(data: Record<string, any>) {
  return request.post("/categories", data);
}

export function updateCategory(id: number, data: Record<string, any>) {
  return request.put(`/categories/${id}`, data);
}

export function deleteCategory(id: number) {
  return request.delete(`/categories/${id}`);
}
