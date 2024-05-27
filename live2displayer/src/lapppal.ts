/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

/**
 * 抽象化平台依赖功能的Cubism平台抽象层。
 *
 * 将文件读取、时间获取等平台依赖函数汇总。
 */
export class LAppPal {
  /**
   * 将文件读取为字节数据
   *
   * @param filePath 要读取的文件路径
   * @param callback 读取完成后的回调函数，包含读取的字节数据和文件大小
   */
  public static loadFileAsBytes(
    filePath: string,
    callback: (arrayBuffer: ArrayBuffer, size: number) => void
  ): void {
    fetch(filePath) // 使用fetch API获取文件
      .then(response => response.arrayBuffer()) // 将响应转换为ArrayBuffer
      .then(arrayBuffer => callback(arrayBuffer, arrayBuffer.byteLength)); // 调用回调函数，传递ArrayBuffer和文件大小
  }

  /**
   * 获取Delta时间（上一帧与当前帧的时间差）
   * @return Delta时间[ms]
   */
  public static getDeltaTime(): number {
    return this.s_deltaTime;
  }

  /**
   * 更新当前时间
   */
  public static updateTime(): void {
    this.s_currentFrame = Date.now(); // 获取当前时间
    this.s_deltaTime = (this.s_currentFrame - this.s_lastFrame) / 1000; // 计算上一帧与当前帧的时间差并转换为秒
    this.s_lastFrame = this.s_currentFrame; // 更新上一帧的时间
  }

  /**
   * 输出消息
   * @param message 要输出的字符串
   */
  public static printMessage(message: string): void {
    console.log(message); // 输出消息到控制台
  }

  static lastUpdate = Date.now(); // 上次更新时间
  static s_currentFrame = 0.0; // 当前帧时间
  static s_lastFrame = 0.0; // 上一帧时间
  static s_deltaTime = 0.0; // Delta时间
}
