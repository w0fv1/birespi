/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { canvas, gl } from './lappglmanager'; // 从lappglmanager模块导入canvas和gl对象

/**
 * 实现精灵（Sprite）的类
 *
 * 管理纹理ID和矩形区域（Rect）
 */
export class LAppSprite {
  /**
   * 构造函数
   * @param x            x坐标
   * @param y            y坐标
   * @param width        宽度
   * @param height       高度
   * @param textureId    纹理ID
   */
  constructor(
    x: number,
    y: number,
    width: number,
    height: number,
    textureId: WebGLTexture
  ) {
    this._rect = new Rect(); // 创建矩形区域对象
    this._rect.left = x - width * 0.5; // 设置矩形左边界
    this._rect.right = x + width * 0.5; // 设置矩形右边界
    this._rect.up = y + height * 0.5; // 设置矩形上边界
    this._rect.down = y - height * 0.5; // 设置矩形下边界
    this._texture = textureId; // 设置纹理ID
    this._vertexBuffer = null; // 顶点缓冲区
    this._uvBuffer = null; // UV缓冲区
    this._indexBuffer = null; // 索引缓冲区

    this._positionLocation = null; // 位置属性位置
    this._uvLocation = null; // UV属性位置
    this._textureLocation = null; // 纹理属性位置

    this._positionArray = null; // 位置数组
    this._uvArray = null; // UV数组
    this._indexArray = null; // 索引数组

    this._firstDraw = true; // 首次绘制标志
  }

  /**
   * 释放资源。
   */
  public release(): void {
    this._rect = null; // 释放矩形对象

    gl.deleteTexture(this._texture); // 删除纹理
    this._texture = null;

    gl.deleteBuffer(this._uvBuffer); // 删除UV缓冲区
    this._uvBuffer = null;

    gl.deleteBuffer(this._vertexBuffer); // 删除顶点缓冲区
    this._vertexBuffer = null;

    gl.deleteBuffer(this._indexBuffer); // 删除索引缓冲区
    this._indexBuffer = null;
  }

  /**
   * 返回纹理。
   */
  public getTexture(): WebGLTexture {
    return this._texture;
  }

  /**
   * 绘制精灵。
   * @param programId 着色器程序ID
   */
  public render(programId: WebGLProgram): void {
    if (this._texture == null) {
      // 纹理未加载完成
      return;
    }

    // 首次绘制时
    if (this._firstDraw) {
      // 获取attribute变量的位置
      this._positionLocation = gl.getAttribLocation(programId, 'position');
      gl.enableVertexAttribArray(this._positionLocation);

      this._uvLocation = gl.getAttribLocation(programId, 'uv');
      gl.enableVertexAttribArray(this._uvLocation);

      // 获取uniform变量的位置
      this._textureLocation = gl.getUniformLocation(programId, 'texture');

      // 注册uniform属性
      gl.uniform1i(this._textureLocation, 0);

      // 初始化UV缓冲区和坐标
      {
        this._uvArray = new Float32Array([
          1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0
        ]);

        // 创建UV缓冲区
        this._uvBuffer = gl.createBuffer();
      }

      // 初始化顶点缓冲区和坐标
      {
        const maxWidth = canvas.width;
        const maxHeight = canvas.height;

        // 顶点数据
        this._positionArray = new Float32Array([
          (this._rect.right - maxWidth * 0.5) / (maxWidth * 0.5),
          (this._rect.up - maxHeight * 0.5) / (maxHeight * 0.5),
          (this._rect.left - maxWidth * 0.5) / (maxWidth * 0.5),
          (this._rect.up - maxHeight * 0.5) / (maxHeight * 0.5),
          (this._rect.left - maxWidth * 0.5) / (maxWidth * 0.5),
          (this._rect.down - maxHeight * 0.5) / (maxHeight * 0.5),
          (this._rect.right - maxWidth * 0.5) / (maxWidth * 0.5),
          (this._rect.down - maxHeight * 0.5) / (maxHeight * 0.5)
        ]);

        // 创建顶点缓冲区
        this._vertexBuffer = gl.createBuffer();
      }

      // 初始化顶点索引缓冲区
      {
        // 索引数据
        this._indexArray = new Uint16Array([0, 1, 2, 3, 2, 0]);

        // 创建索引缓冲区
        this._indexBuffer = gl.createBuffer();
      }

      this._firstDraw = false;
    }

    // 注册UV坐标
    gl.bindBuffer(gl.ARRAY_BUFFER, this._uvBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, this._uvArray, gl.STATIC_DRAW);

    // 注册attribute属性
    gl.vertexAttribPointer(this._uvLocation, 2, gl.FLOAT, false, 0, 0);

    // 注册顶点坐标
    gl.bindBuffer(gl.ARRAY_BUFFER, this._vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, this._positionArray, gl.STATIC_DRAW);

    // 注册attribute属性
    gl.vertexAttribPointer(this._positionLocation, 2, gl.FLOAT, false, 0, 0);

    // 创建顶点索引
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this._indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, this._indexArray, gl.DYNAMIC_DRAW);

    // 绘制模型
    gl.bindTexture(gl.TEXTURE_2D, this._texture);
    gl.drawElements(gl.TRIANGLES, this._indexArray.length, gl.UNSIGNED_SHORT, 0);
  }

  /**
   * 碰撞检测
   * @param pointX x坐标
   * @param pointY y坐标
   */
  public isHit(pointX: number, pointY: number): boolean {
    // 获取画布高度
    const { height } = canvas;

    // Y坐标需要转换
    const y = height - pointY;

    return (
      pointX >= this._rect.left &&
      pointX <= this._rect.right &&
      y <= this._rect.up &&
      y >= this._rect.down
    );
  }

  _texture: WebGLTexture; // 纹理
  _vertexBuffer: WebGLBuffer; // 顶点缓冲区
  _uvBuffer: WebGLBuffer; // UV缓冲区
  _indexBuffer: WebGLBuffer; // 索引缓冲区
  _rect: Rect; // 矩形区域

  _positionLocation: number; // 位置属性位置
  _uvLocation: number; // UV属性位置
  _textureLocation: WebGLUniformLocation; // 纹理属性位置

  _positionArray: Float32Array; // 位置数组
  _uvArray: Float32Array; // UV数组
  _indexArray: Uint16Array; // 索引数组

  _firstDraw: boolean; // 首次绘制标志
}

/**
 * 矩形类
 */
export class Rect {
  public left: number; // 左边界
  public right: number; // 右边界
  public up: number; // 上边界
  public down: number; // 下边界
}
