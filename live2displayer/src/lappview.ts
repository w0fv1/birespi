/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { CubismMatrix44 } from '@framework/math/cubismmatrix44'; // 导入CubismMatrix44模块
import { CubismViewMatrix } from '@framework/math/cubismviewmatrix'; // 导入CubismViewMatrix模块

import * as LAppDefine from './lappdefine'; // 导入LAppDefine模块
import { LAppDelegate } from './lappdelegate'; // 导入LAppDelegate模块
import { canvas, gl } from './lappglmanager'; // 从lappglmanager模块导入canvas和gl对象
import { LAppLive2DManager } from './lapplive2dmanager'; // 导入LAppLive2DManager模块
import { LAppPal } from './lapppal'; // 导入LAppPal模块
import { LAppSprite } from './lappsprite'; // 导入LAppSprite类
import { TextureInfo } from './lapptexturemanager'; // 导入TextureInfo类
import { TouchManager } from './touchmanager'; // 导入TouchManager类

/**
 * 渲染类
 */
export class LAppView {
  /**
   * 构造函数
   */
  constructor() {
    this._programId = null; // 着色器程序ID
    this._back = null; // 背景精灵
    this._gear = null; // 齿轮精灵

    // 管理触摸相关的事件
    this._touchManager = new TouchManager();

    // 用于将设备坐标转换为屏幕坐标的矩阵
    this._deviceToScreen = new CubismMatrix44();

    // 用于处理屏幕显示的缩放和移动的矩阵
    this._viewMatrix = new CubismViewMatrix();
  }

  /**
   * 初始化
   */
  public initialize(): void {
    const { width, height } = canvas;

    const ratio: number = width / height;
    const left: number = -ratio;
    const right: number = ratio;
    const bottom: number = LAppDefine.ViewLogicalLeft;
    const top: number = LAppDefine.ViewLogicalRight;

    this._viewMatrix.setScreenRect(left, right, bottom, top); // 设置屏幕范围，X的左端、X的右端、Y的下端、Y的上端
    this._viewMatrix.scale(LAppDefine.ViewScale, LAppDefine.ViewScale); // 设置缩放比例

    this._deviceToScreen.loadIdentity(); // 加载单位矩阵
    if (width > height) {
      const screenW: number = Math.abs(right - left);
      this._deviceToScreen.scaleRelative(screenW / width, -screenW / width); // 设置比例
    } else {
      const screenH: number = Math.abs(top - bottom);
      this._deviceToScreen.scaleRelative(screenH / height, -screenH / height); // 设置比例
    }
    this._deviceToScreen.translateRelative(-width * 0.5, -height * 0.5); // 设置平移

    // 设置显示范围
    this._viewMatrix.setMaxScale(LAppDefine.ViewMaxScale); // 设置最大缩放比例
    this._viewMatrix.setMinScale(LAppDefine.ViewMinScale); // 设置最小缩放比例

    // 设置显示的最大范围
    this._viewMatrix.setMaxScreenRect(
      LAppDefine.ViewLogicalMaxLeft,
      LAppDefine.ViewLogicalMaxRight,
      LAppDefine.ViewLogicalMaxBottom,
      LAppDefine.ViewLogicalMaxTop
    );
  }

  /**
   * 释放资源
   */
  public release(): void {
    this._viewMatrix = null;
    this._touchManager = null;
    this._deviceToScreen = null;

    if (this._gear) {
      this._gear.release();
      this._gear = null;
    }

    if (this._back) {
      this._back.release();
      this._back = null;
    }

    if (this._programId) {
      gl.deleteProgram(this._programId);
      this._programId = null;
    }
  }

  /**
   * 渲染
   */
  public render(): void {
    gl.useProgram(this._programId); // 使用着色器程序

    if (this._back) {
      this._back.render(this._programId); // 渲染背景
    }
    if (this._gear) {
      this._gear.render(this._programId); // 渲染齿轮
    }

    gl.flush(); // 刷新渲染

    const live2DManager: LAppLive2DManager = LAppLive2DManager.getInstance();

    live2DManager.setViewMatrix(this._viewMatrix); // 设置视图矩阵

    live2DManager.onUpdate(); // 更新模型
  }

  /**
   * 初始化图片
   */
  public initializeSprite(): void {
    const width: number = canvas.width;
    const height: number = canvas.height;

    const textureManager = LAppDelegate.getInstance().getTextureManager();
    const resourcesPath = LAppDefine.ResourcesPath;

    let imageName = '';

    // 初始化背景图片
    imageName = LAppDefine.BackImageName;

    // 异步加载图片，使用回调函数
    const initBackGroundTexture = (textureInfo: TextureInfo): void => {
      const x: number = width * 0.5;
      const y: number = height * 0.5;

      const fwidth = textureInfo.width * 2.0;
      const fheight = height * 0.95;
      this._back = new LAppSprite(x, y, fwidth, fheight, textureInfo.id); // 创建背景精灵
    };

    textureManager.createTextureFromPngFile(
      resourcesPath + imageName,
      false,
      initBackGroundTexture
    );

    // 初始化齿轮图片
    imageName = LAppDefine.GearImageName;
    const initGearTexture = (textureInfo: TextureInfo): void => {
      const x = width - textureInfo.width * 0.5;
      const y = height - textureInfo.height * 0.5;
      const fwidth = textureInfo.width;
      const fheight = textureInfo.height;
      this._gear = new LAppSprite(x, y, fwidth, fheight, textureInfo.id); // 创建齿轮精灵
    };

    textureManager.createTextureFromPngFile(
      resourcesPath + imageName,
      false,
      initGearTexture
    );

    // 创建着色器
    if (this._programId == null) {
      this._programId = LAppDelegate.getInstance().createShader();
    }
  }

  /**
   * 触摸开始事件
   *
   * @param pointX 屏幕X坐标
   * @param pointY 屏幕Y坐标
   */
  public onTouchesBegan(pointX: number, pointY: number): void {
    this._touchManager.touchesBegan(
      pointX * window.devicePixelRatio,
      pointY * window.devicePixelRatio
    );
  }

  /**
   * 触摸移动事件
   *
   * @param pointX 屏幕X坐标
   * @param pointY 屏幕Y坐标
   */
  public onTouchesMoved(pointX: number, pointY: number): void {
    const viewX: number = this.transformViewX(this._touchManager.getX());
    const viewY: number = this.transformViewY(this._touchManager.getY());

    this._touchManager.touchesMoved(
      pointX * window.devicePixelRatio,
      pointY * window.devicePixelRatio
    );

    const live2DManager: LAppLive2DManager = LAppLive2DManager.getInstance();
    live2DManager.onDrag(viewX, viewY);
  }

  /**
   * 触摸结束事件
   *
   * @param pointX 屏幕X坐标
   * @param pointY 屏幕Y坐标
   */
  public onTouchesEnded(pointX: number, pointY: number): void {
    // 触摸结束
    const live2DManager: LAppLive2DManager = LAppLive2DManager.getInstance();
    live2DManager.onDrag(0.0, 0.0);

    {
      // 单次触摸
      const x: number = this._deviceToScreen.transformX(
        this._touchManager.getX()
      ); // 获取逻辑坐标转换后的X坐标
      const y: number = this._deviceToScreen.transformY(
        this._touchManager.getY()
      ); // 获取逻辑坐标转换后的Y坐标

      if (LAppDefine.DebugTouchLogEnable) {
        LAppPal.printMessage(`[APP]touchesEnded x: ${x} y: ${y}`);
      }
      live2DManager.onTap(x, y);

      // 判断是否点击了齿轮
      if (
        this._gear.isHit(
          pointX * window.devicePixelRatio,
          pointY * window.devicePixelRatio
        )
      ) {
        live2DManager.nextScene(); // 切换到下一个场景
      }
    }
  }

  /**
   * 将X坐标转换为View坐标
   *
   * @param deviceX 设备X坐标
   */
  public transformViewX(deviceX: number): number {
    const screenX: number = this._deviceToScreen.transformX(deviceX); // 获取逻辑坐标转换后的X坐标
    return this._viewMatrix.invertTransformX(screenX); // 获取缩放、移动后的X坐标
  }

  /**
   * 将Y坐标转换为View坐标
   *
   * @param deviceY 设备Y坐标
   */
  public transformViewY(deviceY: number): number {
    const screenY: number = this._deviceToScreen.transformY(deviceY); // 获取逻辑坐标转换后的Y坐标
    return this._viewMatrix.invertTransformY(screenY); // 获取缩放、移动后的Y坐标
  }

  /**
   * 将X坐标转换为Screen坐标
   * @param deviceX 设备X坐标
   */
  public transformScreenX(deviceX: number): number {
    return this._deviceToScreen.transformX(deviceX); // 转换为屏幕X坐标
  }

  /**
   * 将Y坐标转换为Screen坐标
   *
   * @param deviceY 设备Y坐标
   */
  public transformScreenY(deviceY: number): number {
    return this._deviceToScreen.transformY(deviceY); // 转换为屏幕Y坐标
  }

  _touchManager: TouchManager; // 触摸管理器
  _deviceToScreen: CubismMatrix44; // 设备到屏幕的矩阵
  _viewMatrix: CubismViewMatrix; // 视图矩阵
  _programId: WebGLProgram; // 着色器程序ID
  _back: LAppSprite; // 背景精灵
  _gear: LAppSprite; // 齿轮精灵
  _changeModel: boolean; // 模型切换标志
  _isClick: boolean; // 点击标志
}
