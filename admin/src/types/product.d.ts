export interface ProductCategory {
  id: number;
  name: string;
  name_en?: string;
  parent_id?: number;
  sort_order: number;
  icon?: string;
  description?: string;
  is_active: boolean;
  children?: ProductCategory[];
}

export interface ProductVariant {
  id: number;
  product_id: number;
  sku?: string;
  name?: string;
  thickness?: number;
  width?: number;
  length?: number;
  density?: number;
  price?: number;
  stock?: number;
  is_active: boolean;
}

export interface ApplicationScenario {
  id: number;
  name: string;
  description?: string;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  model?: string;
  brand?: string;
  description?: string;
  detail_content?: string;
  specs?: Record<string, any>;
  unit?: string;
  reference_price?: number;
  cover_image?: string;
  images?: string[];
  keywords?: string;
  stock: number;
  is_published: boolean;
  is_recommended: boolean;
  category?: ProductCategory;
  scenarios?: ApplicationScenario[];
  variants?: ProductVariant[];
  created_at: string;
  updated_at: string;
}
