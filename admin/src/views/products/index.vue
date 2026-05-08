<template>
  <div class="products">
    <!-- Search & Toolbar -->
    <el-card class="toolbar-card">
      <el-form :inline="true" :model="searchForm" size="default">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="名称/型号/品牌" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-tree-select
            v-model="searchForm.category_id"
            :data="categoryTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="全部分类"
            clearable
            check-strictly
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_published" placeholder="全部" clearable style="width: 120px">
            <el-option label="已上架" :value="true" />
            <el-option label="未上架" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>产品列表 (共 {{ total }} 条)</span>
          <el-button type="primary" @click="openCreate">新增产品</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="产品名称" min-width="160">
          <template #default="{ row }">
            <div class="product-name">
              <el-image v-if="row.cover_image" :src="row.cover_image" style="width:40px;height:40px;border-radius:4px;margin-right:8px" fit="cover" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">{{ row.category?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="model" label="型号" width="120" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="reference_price" label="参考价(元)" width="110" align="right">
          <template #default="{ row }">
            {{ row.reference_price != null ? `¥${row.reference_price} / ${row.unit || '单位'}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" align="right" />
        <el-table-column prop="is_published" label="上架" width="70" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_published" @change="togglePublish(row)" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="is_recommended" label="推荐" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_recommended" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-popconfirm title="确定删除该产品？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchProducts"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑产品' : '新增产品'"
      width="760px"
      destroy-on-close
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="产品名称" prop="name">
              <el-input v-model="form.name" placeholder="如：高密度岩棉板" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属分类" prop="category_id">
              <el-tree-select
                v-model="form.category_id"
                :data="categoryTree"
                :props="{ label: 'name', value: 'id', children: 'children' }"
                placeholder="选择分类"
                check-strictly
                style="width:100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="form.model" placeholder="产品型号/编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" placeholder="品牌名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="参考单价">
              <el-input-number v-model="form.reference_price" :min="0" :precision="2" style="width:100%" placeholder="价格" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="计价单位">
              <el-select v-model="form.unit" placeholder="单位" style="width:100%">
                <el-option label="立方米" value="立方米" />
                <el-option label="平方米" value="平方米" />
                <el-option label="米" value="米" />
                <el-option label="吨" value="吨" />
                <el-option label="卷" value="卷" />
                <el-option label="片" value="片" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存">
              <el-input-number v-model="form.stock" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="产品描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="简短描述" />
        </el-form-item>
        <el-form-item label="详情内容">
          <el-input v-model="form.detail_content" type="textarea" :rows="3" placeholder="富文本详情(HTML/Markdown)" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="封面图URL">
              <el-input v-model="form.cover_image" placeholder="图片链接" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关键词">
              <el-input v-model="form.keywords" placeholder="SEO关键词，逗号分隔" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="应用场景">
          <el-select v-model="form.scenario_ids" multiple placeholder="选择应用场景" style="width:100%">
            <el-option v-for="s in scenarios" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="上架">
              <el-switch v-model="form.is_published" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="推荐">
              <el-switch v-model="form.is_recommended" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- Variants -->
        <el-divider content-position="left">规格变体 (SKU)</el-divider>
        <div v-for="(v, idx) in form.variants" :key="idx" class="variant-row">
          <el-row :gutter="8">
            <el-col :span="4">
              <el-input v-model="v.name" placeholder="变体名" size="small" />
            </el-col>
            <el-col :span="3">
              <el-input v-model="v.thickness" placeholder="厚度mm" size="small" type="number" />
            </el-col>
            <el-col :span="3">
              <el-input v-model="v.density" placeholder="密度" size="small" type="number" />
            </el-col>
            <el-col :span="3">
              <el-input v-model="v.width" placeholder="宽度mm" size="small" type="number" />
            </el-col>
            <el-col :span="3">
              <el-input v-model="v.length" placeholder="长度mm" size="small" type="number" />
            </el-col>
            <el-col :span="4">
              <el-input v-model="v.price" placeholder="价格" size="small" type="number" />
            </el-col>
            <el-col :span="2">
              <el-input v-model="v.stock" placeholder="库存" size="small" type="number" />
            </el-col>
            <el-col :span="2">
              <el-button link type="danger" @click="removeVariant(idx)">删</el-button>
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" link @click="addVariant">+ 添加规格变体</el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="产品详情" width="680px">
      <template v-if="currentProduct">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="产品名称">{{ currentProduct.name }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentProduct.category?.name }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ currentProduct.model || '-' }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ currentProduct.brand || '-' }}</el-descriptions-item>
          <el-descriptions-item label="参考单价">
            {{ currentProduct.reference_price != null ? `¥${currentProduct.reference_price} / ${currentProduct.unit || '单位'}` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="库存">{{ currentProduct.stock }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentProduct.is_published ? 'success' : 'info'">
              {{ currentProduct.is_published ? '已上架' : '未上架' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="推荐">
            {{ currentProduct.is_recommended ? '是' : '否' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentProduct.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="应用场景" :span="2">
            <template v-if="currentProduct.scenarios?.length">
              <el-tag v-for="s in currentProduct.scenarios" :key="s.id" style="margin-right:4px">{{ s.name }}</el-tag>
            </template>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="currentProduct.variants?.length" style="margin-top:16px">
          <h4>规格变体</h4>
          <el-table :data="currentProduct.variants" border size="small" style="margin-top:8px">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="thickness" label="厚度mm" />
            <el-table-column prop="density" label="密度kg/m³" />
            <el-table-column prop="width" label="宽mm" />
            <el-table-column prop="length" label="长mm" />
            <el-table-column prop="price" label="价格" />
            <el-table-column prop="stock" label="库存" />
          </el-table>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from "@/api/product";
import { getCategories } from "@/api/category";
import request from "@/utils/request";

interface VariantForm {
  name: string; thickness: number | null; density: number | null;
  width: number | null; length: number | null; price: number | null; stock: number;
}

interface ProductForm {
  category_id: number | null; name: string; model: string; brand: string;
  description: string; detail_content: string; unit: string | null;
  reference_price: number | null; stock: number; cover_image: string;
  keywords: string; is_published: boolean; is_recommended: boolean;
  scenario_ids: number[]; variants: VariantForm[];
}

const loading = ref(false);
const saving = ref(false);
const tableData = ref<any[]>([]);
const total = ref(0);
const categoryTree = ref<any[]>([]);
const scenarios = ref<any[]>([]);
const dialogVisible = ref(false);
const detailVisible = ref(false);
const currentProduct = ref<any>(null);
const editingId = ref<number | null>(null);
const formRef = ref();

const searchForm = reactive({
  keyword: "", category_id: null as unknown as number, is_published: null as unknown as boolean,
  page: 1, page_size: 20,
});

const emptyForm = (): ProductForm => ({
  category_id: null, name: "", model: "", brand: "",
  description: "", detail_content: "", unit: null,
  reference_price: null, stock: 9999, cover_image: "",
  keywords: "", is_published: false, is_recommended: false,
  scenario_ids: [], variants: [],
});

const form = reactive<ProductForm>(emptyForm());

const rules = {
  name: [{ required: true, message: "请输入产品名称", trigger: "blur" }],
  category_id: [{ required: true, message: "请选择分类", trigger: "change" }],
};

onMounted(() => {
  fetchCategories();
  fetchScenarios();
  fetchProducts();
});

async function fetchCategories() {
  const res: any = await getCategories();
  if (res?.items) categoryTree.value = res.items;
}

async function fetchScenarios() {
  const res: any = await request.get("/scenarios");
  if (res?.items) scenarios.value = res.items;
}

async function fetchProducts() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: searchForm.page, page_size: searchForm.page_size };
    if (searchForm.keyword) params.keyword = searchForm.keyword;
    if (searchForm.category_id) params.category_id = searchForm.category_id;
    if (searchForm.is_published !== null && searchForm.is_published !== undefined)
      params.is_published = searchForm.is_published;

    const res: any = await getProducts(params);
    tableData.value = res?.items || [];
    total.value = res?.total || 0;
  } finally {
    loading.value = false;
  }
}

function handleSearch() { searchForm.page = 1; fetchProducts(); }
function resetSearch() {
  searchForm.keyword = "";
  searchForm.category_id = null as any;
  searchForm.is_published = null as any;
  searchForm.page = 1;
  fetchProducts();
}

function addVariant() {
  form.variants.push({ name: "", thickness: null, density: null, width: null, length: null, price: null, stock: 9999 });
}
function removeVariant(idx: number) { form.variants.splice(idx, 1); }

async function openCreate() {
  editingId.value = null;
  Object.assign(form, emptyForm());
  dialogVisible.value = true;
}

async function openEdit(row: any) {
  editingId.value = row.id;
  const res: any = await getProduct(row.id);
  if (!res) return;
  Object.assign(form, {
    category_id: res.category_id,
    name: res.name,
    model: res.model || "",
    brand: res.brand || "",
    description: res.description || "",
    detail_content: res.detail_content || "",
    unit: res.unit || null,
    reference_price: res.reference_price ?? null,
    stock: res.stock,
    cover_image: res.cover_image || "",
    keywords: res.keywords || "",
    is_published: res.is_published,
    is_recommended: res.is_recommended,
    scenario_ids: (res.scenarios || []).map((s: any) => s.id),
    variants: (res.variants || []).map((v: any) => ({
      name: v.name || "", thickness: v.thickness, density: v.density,
      width: v.width, length: v.length, price: v.price, stock: v.stock,
    })),
  });
  dialogVisible.value = true;
}

function resetForm() {
  Object.assign(form, emptyForm());
  editingId.value = null;
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const payload: any = {
      category_id: form.category_id,
      name: form.name,
      model: form.model || undefined,
      brand: form.brand || undefined,
      description: form.description || undefined,
      detail_content: form.detail_content || undefined,
      unit: form.unit || undefined,
      reference_price: form.reference_price ?? undefined,
      stock: form.stock,
      cover_image: form.cover_image || undefined,
      keywords: form.keywords || undefined,
      is_published: form.is_published,
      is_recommended: form.is_recommended,
      scenario_ids: form.scenario_ids.length ? form.scenario_ids : undefined,
      variants: form.variants.length ? form.variants.map(v => ({
        name: v.name || undefined, thickness: v.thickness ?? undefined,
        density: v.density ?? undefined, width: v.width ?? undefined,
        length: v.length ?? undefined, price: v.price ?? undefined, stock: v.stock,
      })) : undefined,
    };

    if (editingId.value) {
      await updateProduct(editingId.value, payload);
      ElMessage.success("更新成功");
    } else {
      await createProduct(payload);
      ElMessage.success("创建成功");
    }
    dialogVisible.value = false;
    fetchProducts();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(id: number) {
  await deleteProduct(id);
  ElMessage.success("删除成功");
  fetchProducts();
}

async function togglePublish(row: any) {
  await updateProduct(row.id, { is_published: !row.is_published });
  ElMessage.success(row.is_published ? "已下架" : "已上架");
  fetchProducts();
}

function openDetail(row: any) {
  currentProduct.value = row;
  detailVisible.value = true;
}
</script>

<style scoped>
.toolbar-card { margin-bottom: 16px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.product-name { display: flex; align-items: center; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
.variant-row { margin-bottom: 8px; padding: 8px; background: #fafafa; border-radius: 4px; }
</style>
