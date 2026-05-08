<template>
  <div class="categories">
    <el-row :gutter="16">
      <!-- Left: Category Tree -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>分类树</span>
              <el-button type="primary" size="small" @click="openCreate(null)">新增根分类</el-button>
            </div>
          </template>
          <el-tree
            v-loading="loading"
            :data="treeData"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            default-expand-all
            highlight-current
            @node-click="handleNodeClick"
          >
            <template #default="{ data }">
              <span class="tree-node">
                <span>{{ data.name }}</span>
                <span v-if="data.name_en" class="name-en">{{ data.name_en }}</span>
                <span class="tree-actions">
                  <el-button link type="primary" size="small" @click.stop="openCreate(data)">添加子分类</el-button>
                  <el-button link type="primary" size="small" @click.stop="openEdit(data)">编辑</el-button>
                  <el-popconfirm title="确定删除？子分类将上移" @confirm="handleDelete(data.id)">
                    <template #reference>
                      <el-button link type="danger" size="small" @click.stop>删除</el-button>
                    </template>
                  </el-popconfirm>
                </span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- Right: Details -->
      <el-col :span="14">
        <el-card v-if="selectedNode">
          <template #header>
            <span>分类详情: {{ selectedNode.name }}</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ID">{{ selectedNode.id }}</el-descriptions-item>
            <el-descriptions-item label="上级分类">
              {{ findParentName(selectedNode.parent_id) }}
            </el-descriptions-item>
            <el-descriptions-item label="英文名">{{ selectedNode.name_en || '-' }}</el-descriptions-item>
            <el-descriptions-item label="排序号">{{ selectedNode.sort_order }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedNode.is_active ? 'success' : 'info'">
                {{ selectedNode.is_active ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="图标URL">{{ selectedNode.icon || '-' }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ selectedNode.description || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card v-else>
          <el-empty description="请在左侧选择一个分类查看详情" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isCreating ? '新增分类' : '编辑分类'"
      width="520px"
      destroy-on-close
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="上级分类">
          <el-tree-select
            v-model="form.parent_id"
            :data="treeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="不选则为根分类"
            clearable
            check-strictly
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="如：岩棉板" />
        </el-form-item>
        <el-form-item label="英文名称">
          <el-input v-model="form.name_en" placeholder="如：Rock Wool Board" />
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="form.sort_order" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="图标URL">
          <el-input v-model="form.icon" placeholder="图标链接" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="分类描述" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { getCategories, createCategory, updateCategory, deleteCategory } from "@/api/category";

interface CategoryForm {
  name: string;
  name_en: string;
  parent_id: number | null;
  sort_order: number;
  icon: string;
  description: string;
  is_active: boolean;
}

const loading = ref(false);
const saving = ref(false);
const treeData = ref<any[]>([]);
const selectedNode = ref<any>(null);
const dialogVisible = ref(false);
const isCreating = ref(true);
const editingId = ref<number | null>(null);
const formRef = ref();

const form = reactive<CategoryForm>({
  name: "", name_en: "", parent_id: null, sort_order: 0,
  icon: "", description: "", is_active: true,
});

const rules = {
  name: [{ required: true, message: "请输入分类名称", trigger: "blur" }],
};

onMounted(() => fetchTree());

async function fetchTree() {
  loading.value = true;
  try {
    const res: any = await getCategories();
    treeData.value = res?.items || [];
  } finally {
    loading.value = false;
  }
}

function findParentName(parentId: number | null): string {
  if (!parentId) return "无 (根分类)";
  const find = (nodes: any[]): any => {
    for (const n of nodes) {
      if (n.id === parentId) return n;
      if (n.children) {
        const found = find(n.children);
        if (found) return found;
      }
    }
    return null;
  };
  const node = find(treeData.value);
  return node?.name || `ID: ${parentId}`;
}

function handleNodeClick(data: any) {
  selectedNode.value = data;
}

function allNodes(): any[] {
  const result: any[] = [];
  const walk = (nodes: any[]) => {
    for (const n of nodes) {
      result.push(n);
      if (n.children) walk(n.children);
    }
  };
  walk(treeData.value);
  return result;
}

function openCreate(parent: any | null) {
  isCreating.value = true;
  editingId.value = null;
  form.name = "";
  form.name_en = "";
  form.parent_id = parent?.id || null;
  form.sort_order = 0;
  form.icon = "";
  form.description = "";
  form.is_active = true;
  dialogVisible.value = true;
}

function openEdit(node: any) {
  isCreating.value = false;
  editingId.value = node.id;
  form.name = node.name || "";
  form.name_en = node.name_en || "";
  form.parent_id = node.parent_id ?? null;
  form.sort_order = node.sort_order || 0;
  form.icon = node.icon || "";
  form.description = node.description || "";
  form.is_active = node.is_active;
  dialogVisible.value = true;
}

function resetForm() {
  editingId.value = null;
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const payload = {
      name: form.name,
      name_en: form.name_en || undefined,
      parent_id: form.parent_id ?? undefined,
      sort_order: form.sort_order,
      icon: form.icon || undefined,
      description: form.description || undefined,
      is_active: form.is_active,
    };

    if (editingId.value) {
      await updateCategory(editingId.value, payload);
      ElMessage.success("更新成功");
    } else {
      await createCategory(payload);
      ElMessage.success("创建成功");
    }
    dialogVisible.value = false;
    await fetchTree();
  } finally {
    saving.value = false;
  }
}

async function handleDelete(id: number) {
  await deleteCategory(id);
  ElMessage.success("删除成功");
  selectedNode.value = null;
  await fetchTree();
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.tree-node { display: flex; align-items: center; width: 100%; }
.tree-node .name-en { color: #999; font-size: 12px; margin-left: 8px; }
.tree-actions { margin-left: auto; display: flex; gap: 4px; }
</style>
