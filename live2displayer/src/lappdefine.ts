/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { LogLevel } from '@framework/live2dcubismframework'; // 导入Live2D框架的日志级别

/**
 * Sample Appで使用する定数
 * 在示例应用程序中使用的常量
 */

// 画布的宽度和高度像素值，或动态屏幕尺寸（'auto'）。
export const CanvasSize: { width: number; height: number } | 'auto' = 'auto';

// 画面相关常量
export const ViewScale = 1.0; // 视图缩放比例
export const ViewMaxScale = 2.0; // 最大缩放比例
export const ViewMinScale = 0.8; // 最小缩放比例

export const ViewLogicalLeft = -1.0; // 逻辑视图左边界
export const ViewLogicalRight = 1.0; // 逻辑视图右边界
export const ViewLogicalBottom = -1.0; // 逻辑视图下边界
export const ViewLogicalTop = 1.0; // 逻辑视图上边界

export const ViewLogicalMaxLeft = -2.0; // 逻辑视图最大左边界
export const ViewLogicalMaxRight = 2.0; // 逻辑视图最大右边界
export const ViewLogicalMaxBottom = -2.0; // 逻辑视图最大下边界
export const ViewLogicalMaxTop = 2.0; // 逻辑视图最大上边界

// 资源相对路径
export const ResourcesPath = '../../Resources/';

// 模型后面的背景图片文件
export const BackImageName = 'back_class_normal.png';

// 齿轮图标
export const GearImageName = 'icon_gear.png';

// 关闭按钮图标
export const PowerImageName = 'CloseNormal.png';

// 模型定义---------------------------------------------
// 模型所在目录名的数组
// 保证目录名与model3.json文件名一致
export const ModelDir: string[] = [
  'Haru',
  'Hiyori',
  'Mark',
  'Natori',
  'Rice',
  'Mao',
  'Wanko'
];
export const ModelDirSize: number = ModelDir.length; // 模型目录数组的大小

// 与外部定义文件（json）保持一致
export const MotionGroupIdle = 'Idle'; // 待机动作组
export const MotionGroupTapBody = 'TapBody'; // 点击身体时的动作组

// 与外部定义文件（json）保持一致
export const HitAreaNameHead = 'Head'; // 点击区域名称：头部
export const HitAreaNameBody = 'Body'; // 点击区域名称：身体

// 动作的优先级常量
export const PriorityNone = 0; // 无优先级
export const PriorityIdle = 1; // 待机优先级
export const PriorityNormal = 2; // 普通优先级
export const PriorityForce = 3; // 强制优先级

// MOC3一致性验证选项
export const MOCConsistencyValidationEnable = true; // 启用MOC3一致性验证

// 调试日志显示选项
export const DebugLogEnable = true; // 启用调试日志
export const DebugTouchLogEnable = false; // 禁用触摸调试日志

// 框架日志输出的级别设置
export const CubismLoggingLevel: LogLevel = LogLevel.LogLevel_Verbose; // 设置日志级别为详细

// 默认的渲染目标大小
export const RenderTargetWidth = 1900; // 渲染目标宽度
export const RenderTargetHeight = 1000; // 渲染目标高度
