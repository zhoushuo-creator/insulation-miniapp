"""
Seed data: 8 major insulation product categories + subcategories + application scenarios.
Import and call run_seed(async_session) in startup or via script.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.category import ProductCategory, ApplicationScenario

# 8 major categories with subcategories
CATEGORIES = [
    {
        "name": "岩棉板",
        "name_en": "Rock Wool Board",
        "sort_order": 1,
        "description": "以玄武岩为主要原料制成的高效保温材料，防火等级A1级",
        "children": [
            {"name": "普通岩棉板", "sort_order": 1, "description": "标准密度岩棉板，适用于建筑外墙保温"},
            {"name": "高密度岩棉板", "sort_order": 2, "description": "高密度高强度岩棉板，适用于屋面、楼板保温"},
            {"name": "憎水岩棉板", "sort_order": 3, "description": "经特殊工艺处理的憎水型岩棉板，防潮性能优异"},
            {"name": "岩棉管壳", "sort_order": 4, "description": "管道保温专用岩棉管壳"},
        ],
    },
    {
        "name": "玻璃棉",
        "name_en": "Glass Wool",
        "sort_order": 2,
        "description": "以石英砂、长石等为原料制成的纤维状保温材料，质轻柔软",
        "children": [
            {"name": "玻璃棉板", "sort_order": 1, "description": "板状玻璃棉制品，适用于墙体、屋面保温"},
            {"name": "玻璃棉毡", "sort_order": 2, "description": "卷材状玻璃棉，施工便捷，适用于大面积保温"},
            {"name": "玻璃棉管", "sort_order": 3, "description": "管道保温专用玻璃棉管壳"},
            {"name": "超细玻璃棉", "sort_order": 4, "description": "超细纤维玻璃棉，保温性能优异"},
        ],
    },
    {
        "name": "硅酸铝",
        "name_en": "Aluminum Silicate",
        "sort_order": 3,
        "description": "耐高温纤维状保温材料，最高使用温度达1260°C",
        "children": [
            {"name": "硅酸铝板", "sort_order": 1, "description": "板状硅酸铝制品，适用于高温设备保温"},
            {"name": "硅酸铝毡", "sort_order": 2, "description": "毡状硅酸铝制品，施工灵活"},
            {"name": "硅酸铝棉", "sort_order": 3, "description": "散状硅酸铝纤维棉，适用于填充及喷涂"},
            {"name": "硅酸铝管壳", "sort_order": 4, "description": "管道保温专用硅酸铝管壳"},
        ],
    },
    {
        "name": "聚氨酯",
        "name_en": "Polyurethane (PU)",
        "sort_order": 4,
        "description": "硬质聚氨酯泡沫保温材料，导热系数极低，保温性能优异",
        "children": [
            {"name": "聚氨酯板", "sort_order": 1, "description": "预制聚氨酯硬泡板，适用于冷库、屋面保温"},
            {"name": "聚氨酯喷涂", "sort_order": 2, "description": "现场喷涂聚氨酯泡沫，无缝保温层"},
            {"name": "聚氨酯管壳", "sort_order": 3, "description": "管道保温专用聚氨酯管壳"},
        ],
    },
    {
        "name": "挤塑板",
        "name_en": "XPS Board",
        "sort_order": 5,
        "description": "挤塑聚苯乙烯泡沫板，闭孔率高，抗压强度好，吸水率低",
        "children": [
            {"name": "普通挤塑板", "sort_order": 1, "description": "标准挤塑板，适用于建筑外墙、屋面保温"},
            {"name": "高抗压挤塑板", "sort_order": 2, "description": "高抗压强度挤塑板，适用于地坪、冷库地面"},
            {"name": "地暖挤塑板", "sort_order": 3, "description": "地暖专用挤塑板，带铝箔/沟槽"},
        ],
    },
    {
        "name": "橡塑海绵",
        "name_en": "Rubber-Plastic Sponge",
        "sort_order": 6,
        "description": "以丁腈橡胶、聚氯乙烯为主体的闭孔弹性保温材料，防潮性能极佳",
        "children": [
            {"name": "橡塑板", "sort_order": 1, "description": "板状橡塑制品，适用于风管、设备保温"},
            {"name": "橡塑管", "sort_order": 2, "description": "管状橡塑制品，直接包裹管道安装便捷"},
        ],
    },
    {
        "name": "气凝胶",
        "name_en": "Aerogel",
        "sort_order": 7,
        "description": "纳米多孔气凝胶保温材料，导热系数世界最低，超薄高效",
        "children": [
            {"name": "气凝胶毡", "sort_order": 1, "description": "气凝胶复合毡，适用于高温管道、设备保温"},
            {"name": "气凝胶板", "sort_order": 2, "description": "刚性气凝胶板，适用于建筑外墙内保温"},
            {"name": "气凝胶涂料", "sort_order": 3, "description": "气凝胶隔热涂料，适用于异形构件保温"},
        ],
    },
    {
        "name": "保温砂浆",
        "name_en": "Insulation Mortar",
        "sort_order": 8,
        "description": "以无机轻质骨料制成的干粉类保温砂浆，施工抹涂方便",
        "children": [
            {"name": "无机保温砂浆", "sort_order": 1, "description": "以玻化微珠为骨料的无机保温砂浆"},
            {"name": "聚苯颗粒砂浆", "sort_order": 2, "description": "以聚苯颗粒为骨料的保温砂浆"},
            {"name": "胶粉聚苯颗粒", "sort_order": 3, "description": "胶粉聚苯颗粒保温浆料"},
        ],
    },
]

# Application scenarios
SCENARIOS = [
    {"name": "屋顶保温", "description": "建筑屋顶、屋面保温隔热工程", "sort_order": 1},
    {"name": "外墙保温", "description": "建筑外墙外保温、内保温工程", "sort_order": 2},
    {"name": "管道保温", "description": "工业管道、热力管道、空调水管的保温隔热", "sort_order": 3},
    {"name": "工业窑炉", "description": "工业窑炉、锅炉等高温设备的保温隔热", "sort_order": 4},
    {"name": "冷库保温", "description": "冷库、冷藏车、冷链物流的保温隔热", "sort_order": 5},
    {"name": "暖通空调", "description": "暖通空调系统风管、设备的保温隔热", "sort_order": 6},
    {"name": "船舶保温", "description": "船舶舱室、管道、烟囱的保温隔热及防火", "sort_order": 7},
    {"name": "储罐保温", "description": "化工储罐、液化气罐的保温隔热", "sort_order": 8},
]


async def run_seed(db: AsyncSession):
    """Seed categories and scenarios if tables are empty."""

    # Check if categories already exist
    result = await db.execute(select(ProductCategory).limit(1))
    if result.first():
        print("Seed data already exists, skipping...")
        return

    # Seed top-level categories and their children
    for cat_data in CATEGORIES:
        children = cat_data.pop("children", [])
        parent = ProductCategory(**cat_data, parent_id=None, is_active=True)
        db.add(parent)
        await db.flush()

        for child_data in children:
            child = ProductCategory(
                **child_data,
                parent_id=parent.id,
                is_active=True,
            )
            db.add(child)

    # Seed application scenarios
    for scenario_data in SCENARIOS:
        scenario = ApplicationScenario(**scenario_data)
        db.add(scenario)

    await db.flush()
    print(f"Seeded {len(CATEGORIES)} parent categories + subcategories, {len(SCENARIOS)} scenarios")
