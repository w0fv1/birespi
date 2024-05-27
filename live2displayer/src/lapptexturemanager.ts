/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { csmVector, iterator } from '@framework/type/csmvector'; // 从框架中导入csmVector和iterator

import { gl } from './lappglmanager'; // 从lappglmanager模块导入gl对象

/**
 * 纹理管理类
 * 负责图片加载和管理。
 */
export class LAppTextureManager {
  /**
   * 构造函数
   */
  constructor() {
    this._textures = new csmVector<TextureInfo>(); // 初始化纹理信息的容器
  }

  /**
   * 释放所有纹理资源。
   */
  public release(): void {
    for (
      let ite: iterator<TextureInfo> = this._textures.begin();
      ite.notEqual(this._textures.end());
      ite.preIncrement()
    ) {
      gl.deleteTexture(ite.ptr().id); // 删除每个纹理
    }
    this._textures = null; // 清空纹理容器
  }

  /**
   * 加载图片
   *
   * @param fileName 要加载的图片文件路径
   * @param usePremultiply 是否启用Premult处理
   * @param callback 加载完成后的回调函数
   * @return 图片信息，加载失败时返回null
   */
  public createTextureFromPngFile(
    fileName: string,
    usePremultiply: boolean,
    callback: (textureInfo: TextureInfo) => void
  ): void {
    // 查找是否已经加载过该纹理
    for (
      let ite: iterator<TextureInfo> = this._textures.begin();
      ite.notEqual(this._textures.end());
      ite.preIncrement()
    ) {
      if (
        ite.ptr().fileName == fileName &&
        ite.ptr().usePremultply == usePremultiply
      ) {
        // 如果已加载，则使用缓存
        // 重新实例化Image以调用onload
        ite.ptr().img = new Image();
        ite
          .ptr()
          .img.addEventListener('load', (): void => callback(ite.ptr()), {
            passive: true
          });
        ite.ptr().img.src = fileName;
        return;
      }
    }

    // 创建新图片对象并加载
    const img = new Image();
    img.addEventListener(
      'load',
      (): void => {
        // 创建纹理对象
        const tex: WebGLTexture = gl.createTexture();

        // 绑定纹理
        gl.bindTexture(gl.TEXTURE_2D, tex);

        // 设置纹理参数
        gl.texParameteri(
          gl.TEXTURE_2D,
          gl.TEXTURE_MIN_FILTER,
          gl.LINEAR_MIPMAP_LINEAR
        );
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

        // 启用Premult处理
        if (usePremultiply) {
          gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, 1);
        }

        // 将图片数据写入纹理
        gl.texImage2D(
          gl.TEXTURE_2D,
          0,
          gl.RGBA,
          gl.RGBA,
          gl.UNSIGNED_BYTE,
          img
        );

        // 生成mipmap
        gl.generateMipmap(gl.TEXTURE_2D);

        // 解绑纹理
        gl.bindTexture(gl.TEXTURE_2D, null);

        // 创建纹理信息对象
        const textureInfo: TextureInfo = new TextureInfo();
        if (textureInfo != null) {
          textureInfo.fileName = fileName;
          textureInfo.width = img.width;
          textureInfo.height = img.height;
          textureInfo.id = tex;
          textureInfo.img = img;
          textureInfo.usePremultply = usePremultiply;
          this._textures.pushBack(textureInfo); // 将纹理信息添加到容器中
        }

        callback(textureInfo); // 调用回调函数
      },
      { passive: true }
    );
    img.src = fileName; // 设置图片源以触发加载
  }

  /**
   * 释放所有纹理
   *
   * 释放容器中所有的图片资源。
   */
  public releaseTextures(): void {
    for (let i = 0; i < this._textures.getSize(); i++) {
      this._textures.set(i, null); // 清空每个纹理信息
    }

    this._textures.clear(); // 清空容器
  }

  /**
   * 释放指定纹理
   *
   * @param texture 要释放的纹理
   */
  public releaseTextureByTexture(texture: WebGLTexture): void {
    for (let i = 0; i < this._textures.getSize(); i++) {
      if (this._textures.at(i).id != texture) {
        continue;
      }

      this._textures.set(i, null); // 清空指定纹理信息
      this._textures.remove(i); // 从容器中移除
      break;
    }
  }

  /**
   * 释放指定文件路径的纹理
   *
   * @param fileName 要释放的图片文件路径
   */
  public releaseTextureByFilePath(fileName: string): void {
    for (let i = 0; i < this._textures.getSize(); i++) {
      if (this._textures.at(i).fileName == fileName) {
        this._textures.set(i, null); // 清空指定文件路径的纹理信息
        this._textures.remove(i); // 从容器中移除
        break;
      }
    }
  }

  _textures: csmVector<TextureInfo>; // 纹理信息的容器
}

/**
 * 图片信息结构体
 */
export class TextureInfo {
  img: HTMLImageElement; // 图片对象
  id: WebGLTexture = null; // 纹理ID
  width = 0; // 图片宽度
  height = 0; // 图片高度
  usePremultply: boolean; // 是否启用Premult处理
  fileName: string; // 图片文件路径
}
