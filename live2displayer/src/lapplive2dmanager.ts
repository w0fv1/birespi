/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { CubismMatrix44 } from '@framework/math/cubismmatrix44'; // 导入CubismMatrix44模块
import { ACubismMotion } from '@framework/motion/acubismmotion'; // 导入ACubismMotion模块
import { csmVector } from '@framework/type/csmvector'; // 导入csmVector模块

import * as LAppDefine from './lappdefine'; // 导入LAppDefine模块
import { canvas } from './lappglmanager'; // 导入canvas对象
import { LAppModel } from './lappmodel'; // 导入LAppModel类
import { LAppPal } from './lapppal'; // 导入LAppPal模块

export let s_instance: LAppLive2DManager = null; // 声明LAppLive2DManager实例变量

/**
 * 在示例应用程序中管理CubismModel的类
 * 负责模型的生成和销毁、处理点击事件、切换模型等功能。
 */
export class LAppLive2DManager {
  /**
   * 返回类的实例（单例模式）。
   * 如果实例尚未生成，则在内部生成实例。
   *
   * @return 类的实例
   */
  public static getInstance(): LAppLive2DManager {
    if (s_instance == null) {
      s_instance = new LAppLive2DManager();
    }

    return s_instance;
  }

  /**
   * 释放类的实例（单例模式）。
   */
  public static releaseInstance(): void {
    if (s_instance != null) {
      s_instance = void 0;
    }

    s_instance = null;
  }

  /**
   * 返回当前场景中保留的模型。
   *
   * @param no 模型列表的索引值
   * @return 模型的实例。如果索引值超出范围，则返回NULL。
   */
  public getModel(no: number): LAppModel {
    if (no < this._models.getSize()) {
      return this._models.at(no);
    }

    return null;
  }

  /**
   * 释放当前场景中保留的所有模型
   */
  public releaseAllModel(): void {
    for (let i = 0; i < this._models.getSize(); i++) {
      this._models.at(i).release();
      this._models.set(i, null);
    }

    this._models.clear();
  }

  /**
   * 当拖动屏幕时的处理
   *
   * @param x 屏幕的X坐标
   * @param y 屏幕的Y坐标
   */
  public onDrag(x: number, y: number): void {
    for (let i = 0; i < this._models.getSize(); i++) {
      const model: LAppModel = this.getModel(i);

      if (model) {
        model.setDragging(x, y); // 设置拖动坐标
      }
    }
  }

  /**
   * 当点击屏幕时的处理
   *
   * @param x 屏幕的X坐标
   * @param y 屏幕的Y坐标
   */
  public onTap(x: number, y: number): void {
    if (LAppDefine.DebugLogEnable) {
      LAppPal.printMessage(
        `[APP]tap point: {x: ${x.toFixed(2)} y: ${y.toFixed(2)}}`
      );
    }

    for (let i = 0; i < this._models.getSize(); i++) {
      if (this._models.at(i).hitTest(LAppDefine.HitAreaNameHead, x, y)) {
        if (LAppDefine.DebugLogEnable) {
          LAppPal.printMessage(
            `[APP]hit area: [${LAppDefine.HitAreaNameHead}]`
          );
        }
        this._models.at(i).setRandomExpression(); // 设置随机表情
      } else if (this._models.at(i).hitTest(LAppDefine.HitAreaNameBody, x, y)) {
        if (LAppDefine.DebugLogEnable) {
          LAppPal.printMessage(
            `[APP]hit area: [${LAppDefine.HitAreaNameBody}]`
          );
        }
        this._models
          .at(i)
          .startRandomMotion(
            LAppDefine.MotionGroupTapBody,
            LAppDefine.PriorityNormal,
            this._finishedMotion // 设置动作完成后的回调函数
          );
      }
    }
  }

  /**
   * 更新屏幕时的处理
   * 执行模型的更新和绘制处理
   */
  public onUpdate(): void {
    const { width, height } = canvas;

    const modelCount: number = this._models.getSize();

    for (let i = 0; i < modelCount; ++i) {
      const projection: CubismMatrix44 = new CubismMatrix44();
      const model: LAppModel = this.getModel(i);

      if (model.getModel()) {
        if (model.getModel().getCanvasWidth() > 1.0 && width < height) {
          // 当模型横向较长时，按模型的横向尺寸计算缩放
          model.getModelMatrix().setWidth(2.0);
          projection.scale(1.0, width / height);
        } else {
          projection.scale(height / width, 1.0);
        }

        // 如果需要，可以在此进行矩阵乘法
        if (this._viewMatrix != null) {
          projection.multiplyByMatrix(this._viewMatrix);
        }
      }

      model.update(); // 更新模型
      model.draw(projection); // 绘制模型，引用传递，projection会变质
    }
  }

  /**
   * 切换到下一个场景
   * 在示例应用程序中，切换模型集合。
   */
  public nextScene(): void {
    const no: number = (this._sceneIndex + 1) % LAppDefine.ModelDirSize;
    this.changeScene(no);
  }

  /**
   * 切换场景
   * 在示例应用程序中，切换模型集合。
   */
  public changeScene(index: number): void {
    this._sceneIndex = index;
    if (LAppDefine.DebugLogEnable) {
      LAppPal.printMessage(`[APP]model index: ${this._sceneIndex}`);
    }

    // 根据ModelDir[]中的目录名，决定model3.json的路径。
    // 目录名与model3.json的名称保持一致。
    const model: string = LAppDefine.ModelDir[index];
    const modelPath: string = LAppDefine.ResourcesPath + model + '/';
    let modelJsonName: string = LAppDefine.ModelDir[index];
    modelJsonName += '.model3.json';

    this.releaseAllModel();
    this._models.pushBack(new LAppModel());
    this._models.at(0).loadAssets(modelPath, modelJsonName); // 加载模型资源
  }

  /**
   * 设置视图矩阵
   */
  public setViewMatrix(m: CubismMatrix44) {
    for (let i = 0; i < 16; i++) {
      this._viewMatrix.getArray()[i] = m.getArray()[i];
    }
  }

  /**
   * 构造函数
   */
  constructor() {
    this._viewMatrix = new CubismMatrix44(); // 初始化视图矩阵
    this._models = new csmVector<LAppModel>(); // 初始化模型容器
    this._sceneIndex = 0; // 初始化场景索引
    this.changeScene(this._sceneIndex); // 切换到初始场景
  }

  _viewMatrix: CubismMatrix44; // 用于模型绘制的视图矩阵
  _models: csmVector<LAppModel>; // 模型实例的容器
  _sceneIndex: number; // 当前场景的索引值
  // 动作完成后的回调函数
  _finishedMotion = (self: ACubismMotion): void => {
    LAppPal.printMessage('Motion Finished:');
    console.log(self);
  };
}
