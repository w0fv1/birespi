/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

export let canvas: HTMLCanvasElement = null; // 声明HTMLCanvasElement类型的canvas变量
export let gl: WebGLRenderingContext = null; // 声明WebGLRenderingContext类型的gl变量
export let s_instance: LAppGlManager = null; // 声明LAppGlManager实例变量

/**
 * 管理Cubism SDK示例中使用的WebGL的类
 */
export class LAppGlManager {
  /**
   * 返回类的实例（单例模式）。
   * 如果实例尚未生成，则在内部生成实例。
   *
   * @return 类的实例
   */
  public static getInstance(): LAppGlManager {
    if (s_instance == null) {
      s_instance = new LAppGlManager();
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

  constructor() {
    // 创建canvas元素
    canvas = document.createElement('canvas');

    // 初始化WebGL上下文
    // @ts-ignore
    gl = canvas.getContext('webgl2');

    if (!gl) {
      // WebGL初始化失败
      alert('无法初始化WebGL。此浏览器不支持。');
      gl = null;

      document.body.innerHTML =
        '此浏览器不支持<code>&lt;canvas&gt;</code>元素。';
    }
  }

  /**
   * 释放资源。
   */
  public release(): void {}
}
