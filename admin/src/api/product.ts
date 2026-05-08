import request from "@/utils/request";

export function getProducts(params?: Record<string, any>) {
  return request.get("/products", { params });
}

export function getProduct(id: number) {
  return request.get(`/products/${id}`);
}

export function createProduct(data: Record<string, any>) {
  return request.post("/products", data);
}

export function updateProduct(id: number, data: Record<string, any>) {
  return request.put(`/products/${id}`, data);
}

export function deleteProduct(id: number) {
  return request.delete(`/products/${id}`);
}
