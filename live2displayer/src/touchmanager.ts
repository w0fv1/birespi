/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

export class TouchManager {
  /**
   * 构造函数
   */
  constructor() {
    this._startX = 0.0; // 初始触摸的X坐标
    this._startY = 0.0; // 初始触摸的Y坐标
    this._lastX = 0.0; // 最后一次触摸的X坐标
    this._lastY = 0.0; // 最后一次触摸的Y坐标
    this._lastX1 = 0.0; // 双指触摸时，第一个触摸点的X坐标
    this._lastY1 = 0.0; // 双指触摸时，第一个触摸点的Y坐标
    this._lastX2 = 0.0; // 双指触摸时，第二个触摸点的X坐标
    this._lastY2 = 0.0; // 双指触摸时，第二个触摸点的Y坐标
    this._lastTouchDistance = 0.0; // 双指触摸时，两触摸点之间的距离
    this._deltaX = 0.0; // X方向的移动距离
    this._deltaY = 0.0; // Y方向的移动距离
    this._scale = 1.0; // 缩放比例
    this._touchSingle = false; // 是否为单指触摸
    this._flipAvailable = false; // 是否可以进行翻转
  }

  /**
   * 获取最后一次触摸的中心X坐标
   */
  public getCenterX(): number {
    return this._lastX;
  }

  /**
   * 获取最后一次触摸的中心Y坐标
   */
  public getCenterY(): number {
    return this._lastY;
  }

  /**
   * 获取X方向的移动距离
   */
  public getDeltaX(): number {
    return this._deltaX;
  }

  /**
   * 获取Y方向的移动距离
   */
  public getDeltaY(): number {
    return this._deltaY;
  }

  /**
   * 获取初始触摸的X坐标
   */
  public getStartX(): number {
    return this._startX;
  }

  /**
   * 获取初始触摸的Y坐标
   */
  public getStartY(): number {
    return this._startY;
  }

  /**
   * 获取缩放比例
   */
  public getScale(): number {
    return this._scale;
  }

  /**
   * 获取最后一次触摸的X坐标
   */
  public getX(): number {
    return this._lastX;
  }

  /**
   * 获取最后一次触摸的Y坐标
   */
  public getY(): number {
    return this._lastY;
  }

  /**
   * 获取双指触摸时第一个触摸点的X坐标
   */
  public getX1(): number {
    return this._lastX1;
  }

  /**
   * 获取双指触摸时第一个触摸点的Y坐标
   */
  public getY1(): number {
    return this._lastY1;
  }

  /**
   * 获取双指触摸时第二个触摸点的X坐标
   */
  public getX2(): number {
    return this._lastX2;
  }

  /**
   * 获取双指触摸时第二个触摸点的Y坐标
   */
  public getY2(): number {
    return this._lastY2;
  }

  /**
   * 是否为单指触摸
   */
  public isSingleTouch(): boolean {
    return this._touchSingle;
  }

  /**
   * 是否可以进行翻转
   */
  public isFlickAvailable(): boolean {
    return this._flipAvailable;
  }

  /**
   * 禁用翻转
   */
  public disableFlick(): void {
    this._flipAvailable = false;
  }

  /**
   * 触摸开始时的事件
   * @param deviceX 触摸点的X坐标
   * @param deviceY 触摸点的Y坐标
   */
  public touchesBegan(deviceX: number, deviceY: number): void {
    this._lastX = deviceX;
    this._lastY = deviceY;
    this._startX = deviceX;
    this._startY = deviceY;
    this._lastTouchDistance = -1.0;
    this._flipAvailable = true;
    this._touchSingle = true;
  }

  /**
   * 触摸移动时的事件
   * @param deviceX 触摸点的X坐标
   * @param deviceY 触摸点的Y坐标
   */
  public touchesMoved(deviceX: number, deviceY: number): void {
    this._lastX = deviceX;
    this._lastY = deviceY;
    this._lastTouchDistance = -1.0;
    this._touchSingle = true;
  }

  /**
   * 获取翻转距离
   * @return 翻转距离
   */
  public getFlickDistance(): number {
    return this.calculateDistance(
      this._startX,
      this._startY,
      this._lastX,
      this._lastY
    );
  }

  /**
   * 计算两点之间的距离
   *
   * @param x1 第一个点的X坐标
   * @param y1 第一个点的Y坐标
   * @param x2 第二个点的X坐标
   * @param y2 第二个点的Y坐标
   */
  public calculateDistance(
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): number {
    return Math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
  }

  /**
   * 计算移动量
   * 当移动方向相同时，返回较小的移动量；当移动方向不同时，返回0。
   *
   * @param v1 第一个移动量
   * @param v2 第二个移动量
   * @return 较小的移动量
   */
  public calculateMovingAmount(v1: number, v2: number): number {
    if (v1 > 0.0 != v2 > 0.0) {
      return 0.0;
    }

    const sign: number = v1 > 0.0 ? 1.0 : -1.0;
    const absoluteValue1 = Math.abs(v1);
    const absoluteValue2 = Math.abs(v2);
    return (
      sign * (absoluteValue1 < absoluteValue2 ? absoluteValue1 : absoluteValue2)
    );
  }

  _startY: number; // 初始触摸的Y坐标
  _startX: number; // 初始触摸的X坐标
  _lastX: number; // 最后一次触摸的X坐标
  _lastY: number; // 最后一次触摸的Y坐标
  _lastX1: number; // 双指触摸时，第一个触摸点的X坐标
  _lastY1: number; // 双指触摸时，第一个触摸点的Y坐标
  _lastX2: number; // 双指触摸时，第二个触摸点的X坐标
  _lastY2: number; // 双指触摸时，第二个触摸点的Y坐标
  _lastTouchDistance: number; // 双指触摸时，两触摸点之间的距离
  _deltaX: number; // X方向的移动距离
  _deltaY: number; // Y方向的移动距离
  _scale: number; // 缩放比例
  _touchSingle: boolean; // 是否为单指触摸
  _flipAvailable: boolean; // 是否可以进行翻转
}
