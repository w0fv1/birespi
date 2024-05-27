/**
 * Copyright(c) Live2D Inc. All rights reserved.
 *
 * Use of this source code is governed by the Live2D Open Software license
 * that can be found at https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html.
 */
import { LAppDelegate } from "./lappdelegate"; // 导入LAppDelegate模块
import * as LAppDefine from "./lappdefine"; // 导入LAppDefine模块
import { LAppGlManager } from "./lappglmanager"; // 导入LAppGlManager模块

/**
 * 浏览器加载后的处理
 */
window.addEventListener(
  "load", // 监听window的load事件
  (): void => {
    // 初始化WebGL并创建应用程序实例
    if (
      !LAppGlManager.getInstance() || // 如果没有获取到LAppGlManager实例
      !LAppDelegate.getInstance().initialize() // 或者LAppDelegate实例初始化失败
    ) {
      return; // 则不执行后续代码
    }

    LAppDelegate.getInstance().run(); // 运行LAppDelegate实例
  },
  { passive: true }, // 设置为被动模式，提升滚动性能
);

/**
 * 浏览器卸载前的处理
 */
window.addEventListener(
  "beforeunload", // 监听window的beforeunload事件
  (): void => LAppDelegate.releaseInstance(), // 释放LAppDelegate实例
  { passive: true }, // 设置为被动模式
);

/**
 * 处理屏幕大小变化时的操作
 */
window.addEventListener(
  "resize", // 监听window的resize事件
  () => {
    if (LAppDefine.CanvasSize === "auto") { // 如果CanvasSize设置为'auto'
      LAppDelegate.getInstance().onResize(); // 调用LAppDelegate实例的onResize方法
    }
  },
  { passive: true }, // 设置为被动模式
);
