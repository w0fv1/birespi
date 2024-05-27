/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { CubismFramework, Option } from "@framework/live2dcubismframework"; // 导入CubismFramework和Option模块

import * as LAppDefine from "./lappdefine"; // 导入LAppDefine模块
import { LAppLive2DManager } from "./lapplive2dmanager"; // 导入LAppLive2DManager模块
import { LAppPal } from "./lapppal"; // 导入LAppPal模块
import { LAppTextureManager } from "./lapptexturemanager"; // 导入LAppTextureManager模块
import { LAppView } from "./lappview"; // 导入LAppView模块
import { canvas, gl } from "./lappglmanager"; // 导入canvas和WebGL上下文gl

export let s_instance: LAppDelegate = null; // 声明LAppDelegate实例变量
export let frameBuffer: WebGLFramebuffer = null; // 声明WebGL帧缓冲变量

/**
 * 应用程序类。
 * 管理Cubism SDK。
 */
export class LAppDelegate {
  /**
   * 返回类的实例（单例模式）。
   * 如果实例尚未生成，则在内部生成实例。
   *
   * @return 类的实例
   */
  public static getInstance(): LAppDelegate {
    if (s_instance == null) {
      s_instance = new LAppDelegate();
    }

    return s_instance;
  }

  /**
   * 释放类的实例（单例模式）。
   */
  public static releaseInstance(): void {
    if (s_instance != null) {
      s_instance.release();
    }

    s_instance = null;
  }

  /**
   * 初始化应用程序所需的资源。
   */
  public initialize(): boolean {
    // 将canvas添加到DOM中
    document.body.appendChild(canvas);

    if (LAppDefine.CanvasSize === "auto") {
      this._resizeCanvas();
    } else {
      canvas.width = LAppDefine.CanvasSize.width;
      canvas.height = LAppDefine.CanvasSize.height;
    }

    if (!frameBuffer) {
      frameBuffer = gl.getParameter(gl.FRAMEBUFFER_BINDING);
    }

    // 启用混合模式
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    const supportTouch: boolean = "ontouchend" in canvas;

    if (supportTouch) {
      // 注册触摸相关的回调函数
      canvas.addEventListener("touchstart", onTouchBegan, { passive: true });
      canvas.addEventListener("touchmove", onTouchMoved, { passive: true });
      canvas.addEventListener("touchend", onTouchEnded, { passive: true });
      canvas.addEventListener("touchcancel", onTouchCancel, { passive: true });
    } else {
      // 注册鼠标相关的回调函数
      canvas.addEventListener("mousedown", onClickBegan, { passive: true });
      canvas.addEventListener("mousemove", onMouseMoved, { passive: true });
      canvas.addEventListener("mouseup", onClickEnded, { passive: true });
    }

    // 初始化AppView
    this._view.initialize();

    // 初始化Cubism SDK
    this.initializeCubism();

    return true;
  }

  /**
   * 调整画布大小并重新初始化视图。
   */
  public onResize(): void {
    this._resizeCanvas();
    this._view.initialize();
    this._view.initializeSprite();
  }

  /**
   * 释放资源。
   */
  public release(): void {
    this._textureManager.release();
    this._textureManager = null;

    this._view.release();
    this._view = null;

    // 释放资源
    LAppLive2DManager.releaseInstance();

    // 释放Cubism SDK
    CubismFramework.dispose();
  }

  /**
   * 执行处理。
   */
  public run(): void {
    // 主循环
    const loop = (): void => {
      // 检查实例是否存在
      if (s_instance == null) {
        return;
      }

      // 更新时间
      LAppPal.updateTime();

      // 初始化屏幕
      gl.clearColor(0.0, 0.0, 0.0, 1.0);

      // 启用深度测试
      gl.enable(gl.DEPTH_TEST);

      // 近处物体覆盖远处物体
      gl.depthFunc(gl.LEQUAL);

      // 清除颜色和深度缓冲区
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

      gl.clearDepth(1.0);

      // 启用混合模式
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

      // 更新绘制
      this._view.render();

      // 递归调用以实现循环
      requestAnimationFrame(loop);
    };
    loop();
  }

  /**
   * 注册着色器。
   */
  public createShader(): WebGLProgram {
    // 编译顶点着色器
    const vertexShaderId = gl.createShader(gl.VERTEX_SHADER);

    if (vertexShaderId == null) {
      LAppPal.printMessage("failed to create vertexShader");
      return null;
    }

    const vertexShader: string = "precision mediump float;" +
      "attribute vec3 position;" +
      "attribute vec2 uv;" +
      "varying vec2 vuv;" +
      "void main(void)" +
      "{" +
      "   gl_Position = vec4(position, 1.0);" +
      "   vuv = uv;" +
      "}";

    gl.shaderSource(vertexShaderId, vertexShader);
    gl.compileShader(vertexShaderId);

    // 编译片段着色器
    const fragmentShaderId = gl.createShader(gl.FRAGMENT_SHADER);

    if (fragmentShaderId == null) {
      LAppPal.printMessage("failed to create fragmentShader");
      return null;
    }

    const fragmentShader: string = "precision mediump float;" +
      "varying vec2 vuv;" +
      "uniform sampler2D texture;" +
      "void main(void)" +
      "{" +
      "   gl_FragColor = texture2D(texture, vuv);" +
      "}";

    gl.shaderSource(fragmentShaderId, fragmentShader);
    gl.compileShader(fragmentShaderId);

    // 创建程序对象
    const programId = gl.createProgram();
    gl.attachShader(programId, vertexShaderId);
    gl.attachShader(programId, fragmentShaderId);

    gl.deleteShader(vertexShaderId);
    gl.deleteShader(fragmentShaderId);

    // 链接程序
    gl.linkProgram(programId);

    gl.useProgram(programId);

    return programId;
  }

  /**
   * 获取View信息。
   */
  public getView(): LAppView {
    return this._view;
  }

  public getTextureManager(): LAppTextureManager {
    return this._textureManager;
  }

  /**
   * 构造函数
   */
  constructor() {
    this._captured = false;
    this._mouseX = 0.0;
    this._mouseY = 0.0;
    this._isEnd = false;

    this._cubismOption = new Option();
    this._view = new LAppView();
    this._textureManager = new LAppTextureManager();
  }

  /**
   * 初始化Cubism SDK
   */
  public initializeCubism(): void {
    // 设置Cubism
    this._cubismOption.logFunction = LAppPal.printMessage;
    this._cubismOption.loggingLevel = LAppDefine.CubismLoggingLevel;
    CubismFramework.startUp(this._cubismOption);

    // 初始化Cubism
    CubismFramework.initialize();

    // 加载模型
    LAppLive2DManager.getInstance();

    LAppPal.updateTime();

    this._view.initializeSprite();
  }

  /**
   * 将画布调整为全屏。
   */
  private _resizeCanvas(): void {
    canvas.width = canvas.clientWidth * window.devicePixelRatio;
    canvas.height = canvas.clientHeight * window.devicePixelRatio;
    gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
  }

  _cubismOption: Option; // Cubism SDK选项
  _view: LAppView; // 视图信息
  _captured: boolean; // 是否在点击中
  _mouseX: number; // 鼠标X坐标
  _mouseY: number; // 鼠标Y坐标
  _isEnd: boolean; // 应用程序是否结束
  _textureManager: LAppTextureManager; // 纹理管理器
}

/**
 * 当点击时调用。
 */
function onClickBegan(e: MouseEvent): void {
  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }
  LAppDelegate.getInstance()._captured = true;

  const posX: number = e.pageX;
  const posY: number = e.pageY;

  LAppDelegate.getInstance()._view.onTouchesBegan(posX, posY);
}

/**
 * 当鼠标

指针移动时调用。
 */
function onMouseMoved(e: MouseEvent): void {
  if (!LAppDelegate.getInstance()._captured) {
    return;
  }

  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  const rect = (e.target as Element).getBoundingClientRect();
  const posX: number = e.clientX - rect.left;
  const posY: number = e.clientY - rect.top;

  LAppDelegate.getInstance()._view.onTouchesMoved(posX, posY);
}

/**
 * 当点击结束时调用。
 */
function onClickEnded(e: MouseEvent): void {
  LAppDelegate.getInstance()._captured = false;
  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  const rect = (e.target as Element).getBoundingClientRect();
  const posX: number = e.clientX - rect.left;
  const posY: number = e.clientY - rect.top;

  LAppDelegate.getInstance()._view.onTouchesEnded(posX, posY);
}

/**
 * 当触摸开始时调用。
 */
function onTouchBegan(e: TouchEvent): void {
  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  LAppDelegate.getInstance()._captured = true;

  const posX = e.changedTouches[0].pageX;
  const posY = e.changedTouches[0].pageY;

  LAppDelegate.getInstance()._view.onTouchesBegan(posX, posY);
}

/**
 * 当滑动时调用。
 */
function onTouchMoved(e: TouchEvent): void {
  if (!LAppDelegate.getInstance()._captured) {
    return;
  }

  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  const rect = (e.target as Element).getBoundingClientRect();

  const posX = e.changedTouches[0].clientX - rect.left;
  const posY = e.changedTouches[0].clientY - rect.top;

  LAppDelegate.getInstance()._view.onTouchesMoved(posX, posY);
}

/**
 * 当触摸结束时调用。
 */
function onTouchEnded(e: TouchEvent): void {
  LAppDelegate.getInstance()._captured = false;

  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  const rect = (e.target as Element).getBoundingClientRect();

  const posX = e.changedTouches[0].clientX - rect.left;
  const posY = e.changedTouches[0].clientY - rect.top;

  LAppDelegate.getInstance()._view.onTouchesEnded(posX, posY);
}

/**
 * 当触摸取消时调用。
 */
function onTouchCancel(e: TouchEvent): void {
  LAppDelegate.getInstance()._captured = false;

  if (!LAppDelegate.getInstance()._view) {
    LAppPal.printMessage("view notfound");
    return;
  }

  const rect = (e.target as Element).getBoundingClientRect();

  const posX = e.changedTouches[0].clientX - rect.left;
  const posY = e.changedTouches[0].clientY - rect.top;

  LAppDelegate.getInstance()._view.onTouchesEnded(posX, posY);
}
