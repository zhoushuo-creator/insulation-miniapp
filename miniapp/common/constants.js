/**
 * 保温材料小程序常量定义
 */

// 防火等级选项
export const FIRE_RATINGS = [
  { value: "A1", label: "A1级 (不燃)" },
  { value: "A2", label: "A2级 (不燃)" },
  { value: "B1", label: "B1级 (难燃)" },
  { value: "B2", label: "B2级 (可燃)" },
];

// 订单状态
export const ORDER_STATUS = {
  pending: { label: "待付款", color: "#f0ad4e" },
  paid: { label: "已付款", color: "#007aff" },
  shipped: { label: "已发货", color: "#4cd964" },
  completed: { label: "已完成", color: "#909399" },
  cancelled: { label: "已取消", color: "#dd524d" },
};

// 温度选项 (用于筛选)
export const TEMP_RANGES = [
  { value: "low", label: "低温 (-200°C ~ 0°C)", min: -200, max: 0 },
  { value: "normal", label: "常温 (0°C ~ 100°C)", min: 0, max: 100 },
  { value: "mid", label: "中温 (100°C ~ 400°C)", min: 100, max: 400 },
  { value: "high", label: "高温 (400°C ~ 1260°C)", min: 400, max: 1260 },
];

// 常见应用场景快速选项
export const QUICK_SCENARIOS = [
  { value: "屋顶", label: "屋顶保温" },
  { value: "外墙", label: "外墙保温" },
  { value: "管道", label: "管道保温" },
  { value: "工业", label: "工业窑炉" },
  { value: "冷库", label: "冷库保温" },
  { value: "暖通", label: "暖通空调" },
  { value: "船舶", label: "船舶保温" },
  { value: "储罐", label: "储罐保温" },
];
