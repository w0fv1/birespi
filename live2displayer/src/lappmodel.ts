/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

import { CubismDefaultParameterId } from "@framework/cubismdefaultparameterid";
import { CubismModelSettingJson } from "@framework/cubismmodelsettingjson";
import {
  BreathParameterData,
  CubismBreath,
} from "@framework/effect/cubismbreath";
import { CubismEyeBlink } from "@framework/effect/cubismeyeblink";
import { ICubismModelSetting } from "@framework/icubismmodelsetting";
import { CubismIdHandle } from "@framework/id/cubismid";
import { CubismFramework } from "@framework/live2dcubismframework";
import { CubismMatrix44 } from "@framework/math/cubismmatrix44";
import { CubismUserModel } from "@framework/model/cubismusermodel";
import {
  ACubismMotion,
  FinishedMotionCallback,
} from "@framework/motion/acubismmotion";
import { CubismMotion } from "@framework/motion/cubismmotion";
import {
  CubismMotionQueueEntryHandle,
  InvalidMotionQueueEntryHandleValue,
} from "@framework/motion/cubismmotionqueuemanager";
import { csmMap } from "@framework/type/csmmap";
import { csmRect } from "@framework/type/csmrectf";
import { csmString } from "@framework/type/csmstring";
import { csmVector } from "@framework/type/csmvector";
import {
  CSM_ASSERT,
  CubismLogError,
  CubismLogInfo,
} from "@framework/utils/cubismdebug";

import * as LAppDefine from "./lappdefine";
import { frameBuffer, LAppDelegate } from "./lappdelegate";
import { canvas, gl } from "./lappglmanager";
import { LAppPal } from "./lapppal";
import { TextureInfo } from "./lapptexturemanager";
import { LAppWavFileHandler } from "./lappwavfilehandler";
import { CubismMoc } from "@framework/model/cubismmoc";

enum LoadStep {
  LoadAssets,
  LoadModel,
  WaitLoadModel,
  LoadExpression,
  WaitLoadExpression,
  LoadPhysics,
  WaitLoadPhysics,
  LoadPose,
  WaitLoadPose,
  SetupEyeBlink,
  SetupBreath,
  LoadUserData,
  WaitLoadUserData,
  SetupEyeBlinkIds,
  SetupLipSyncIds,
  SetupLayout,
  LoadMotion,
  WaitLoadMotion,
  CompleteInitialize,
  CompleteSetupModel,
  LoadTexture,
  WaitLoadTexture,
  CompleteSetup,
}

/**
 * 用户使用的模型实现类
 * 该类负责模型的生成、功能组件的生成、更新处理和渲染的调用。
 */
export class LAppModel extends CubismUserModel {
  /**
   * 从指定的目录和文件路径加载model3.json并生成模型
   * @param dir 模型所在目录
   * @param fileName 模型文件名
   */
  public loadAssets(dir: string, fileName: string): void {
    this._modelHomeDir = dir;

    fetch(`${this._modelHomeDir}${fileName}`)
      .then((response) => response.arrayBuffer())
      .then((arrayBuffer) => {
        const setting: ICubismModelSetting = new CubismModelSettingJson(
          arrayBuffer,
          arrayBuffer.byteLength,
        );

        // 更新状态
        this._state = LoadStep.LoadModel;

        // 保存结果
        this.setupModel(setting);
      })
      .catch((error) => {
        // 如果在读取model3.json时发生错误，无法进行渲染，因此不进行设置并捕获错误
        CubismLogError(`无法加载文件 ${this._modelHomeDir}${fileName}`);
      });
  }

  /**
   * 从model3.json生成模型。
   * 根据model3.json的描述生成模型、运动、物理等组件。
   *
   * @param setting ICubismModelSetting实例
   */
  private setupModel(setting: ICubismModelSetting): void {
    this._updating = true;
    this._initialized = false;

    this._modelSetting = setting;

    // CubismModel
    if (this._modelSetting.getModelFileName() != "") {
      const modelFileName = this._modelSetting.getModelFileName();

      fetch(`${this._modelHomeDir}${modelFileName}`)
        .then((response) => {
          if (response.ok) {
            return response.arrayBuffer();
          } else if (response.status >= 400) {
            CubismLogError(
              `无法加载文件 ${this._modelHomeDir}${modelFileName}`,
            );
            return new ArrayBuffer(0);
          }
        })
        .then((arrayBuffer) => {
          this.loadModel(arrayBuffer, this._mocConsistency);
          this._state = LoadStep.LoadExpression;

          // 回调
          loadCubismExpression();
        });

      this._state = LoadStep.WaitLoadModel;
    } else {
      LAppPal.printMessage("模型数据不存在。");
    }

    // 表情
    const loadCubismExpression = (): void => {
      if (this._modelSetting.getExpressionCount() > 0) {
        const count: number = this._modelSetting.getExpressionCount();

        for (let i = 0; i < count; i++) {
          const expressionName = this._modelSetting.getExpressionName(i);
          const expressionFileName = this._modelSetting.getExpressionFileName(
            i,
          );

          fetch(`${this._modelHomeDir}${expressionFileName}`)
            .then((response) => {
              if (response.ok) {
                return response.arrayBuffer();
              } else if (response.status >= 400) {
                CubismLogError(
                  `无法加载文件 ${this._modelHomeDir}${expressionFileName}`,
                );
                // 即使文件不存在，response也不会返回null，因此用空的ArrayBuffer处理
                return new ArrayBuffer(0);
              }
            })
            .then((arrayBuffer) => {
              const motion: ACubismMotion = this.loadExpression(
                arrayBuffer,
                arrayBuffer.byteLength,
                expressionName,
              );

              if (this._expressions.getValue(expressionName) != null) {
                ACubismMotion.delete(
                  this._expressions.getValue(expressionName),
                );
                this._expressions.setValue(expressionName, null);
              }

              this._expressions.setValue(expressionName, motion);

              this._expressionCount++;

              if (this._expressionCount >= count) {
                this._state = LoadStep.LoadPhysics;

                // 回调
                loadCubismPhysics();
              }
            });
        }
        this._state = LoadStep.WaitLoadExpression;
      } else {
        this._state = LoadStep.LoadPhysics;

        // 回调
        loadCubismPhysics();
      }
    };

    // 物理
    const loadCubismPhysics = (): void => {
      if (this._modelSetting.getPhysicsFileName() != "") {
        const physicsFileName = this._modelSetting.getPhysicsFileName();

        fetch(`${this._modelHomeDir}${physicsFileName}`)
          .then((response) => {
            if (response.ok) {
              return response.arrayBuffer();
            } else if (response.status >= 400) {
              CubismLogError(
                `无法加载文件 ${this._modelHomeDir}${physicsFileName}`,
              );
              return new ArrayBuffer(0);
            }
          })
          .then((arrayBuffer) => {
            this.loadPhysics(arrayBuffer, arrayBuffer.byteLength);

            this._state = LoadStep.LoadPose;

            // 回调
            loadCubismPose();
          });
        this._state = LoadStep.WaitLoadPhysics;
      } else {
        this._state = LoadStep.LoadPose;

        // 回调
        loadCubismPose();
      }
    };

    // 姿势
    const loadCubismPose = (): void => {
      if (this._modelSetting.getPoseFileName() != "") {
        const poseFileName = this._modelSetting.getPoseFileName();

        fetch(`${this._modelHomeDir}${poseFileName}`)
          .then((response) => {
            if (response.ok) {
              return response.arrayBuffer();
            } else if (response.status >= 400) {
              CubismLogError(
                `无法加载文件 ${this._modelHomeDir}${poseFileName}`,
              );
              return new ArrayBuffer(0);
            }
          })
          .then((arrayBuffer) => {
            this.loadPose(arrayBuffer, arrayBuffer.byteLength);

            this._state = LoadStep.SetupEyeBlink;

            // 回调
            setupEyeBlink();
          });
        this._state = LoadStep.WaitLoadPose;
      } else {
        this._state = LoadStep.SetupEyeBlink;

        // 回调
        setupEyeBlink();
      }
    };

    // 眨眼
    const setupEyeBlink = (): void => {
      if (this._modelSetting.getEyeBlinkParameterCount() > 0) {
        this._eyeBlink = CubismEyeBlink.create(this._modelSetting);
        this._state = LoadStep.SetupBreath;
      }

      // 回调
      setupBreath();
    };

    // 呼吸
    const setupBreath = (): void => {
      this._breath = CubismBreath.create();

      const breathParameters: csmVector<BreathParameterData> = new csmVector();
      breathParameters.pushBack(
        new BreathParameterData(this._idParamAngleX, 0.0, 15.0, 6.5345, 0.5),
      );
      breathParameters.pushBack(
        new BreathParameterData(this._idParamAngleY, 0.0, 8.0, 3.5345, 0.5),
      );
      breathParameters.pushBack(
        new BreathParameterData(this._idParamAngleZ, 0.0, 10.0, 5.5345, 0.5),
      );
      breathParameters.pushBack(
        new BreathParameterData(
          this._idParamBodyAngleX,
          0.0,
          4.0,
          15.5345,
          0.5,
        ),
      );
      breathParameters.pushBack(
        new BreathParameterData(
          CubismFramework.getIdManager().getId(
            CubismDefaultParameterId.ParamBreath,
          ),
          0.5,
          0.5,
          3.2345,
          1,
        ),
      );

      this._breath.setParameters(breathParameters);
      this._state = LoadStep.LoadUserData;

      // 回调
      loadUserData();
    };

    // 用户数据
    const loadUserData = (): void => {
      if (this._modelSetting.getUserDataFile() != "") {
        const userDataFile = this._modelSetting.getUserDataFile();

        fetch(`${this._modelHomeDir}${userDataFile}`)
          .then((response) => {
            if (response.ok) {
              return response.arrayBuffer();
            } else if (response.status >= 400) {
              CubismLogError(
                `无法加载文件 ${this._modelHomeDir}${userDataFile}`,
              );
              return new ArrayBuffer(0);
            }
          })
          .then((arrayBuffer) => {
            this.loadUserData(arrayBuffer, arrayBuffer.byteLength);

            this._state = LoadStep.SetupEyeBlinkIds;

            // 回调
            setupEyeBlinkIds();
          });

        this._state = LoadStep.WaitLoadUserData;
      } else {
        this._state = LoadStep.SetupEyeBlinkIds;

        // 回调
        setupEyeBlinkIds();
      }
    };

    // EyeBlinkIds
    const setupEyeBlinkIds = (): void => {
      const eyeBlinkIdCount: number = this._modelSetting
        .getEyeBlinkParameterCount();

      for (let i = 0; i < eyeBlinkIdCount; ++i) {
        this._eyeBlinkIds.pushBack(
          this._modelSetting.getEyeBlinkParameterId(i),
        );
      }

      this._state = LoadStep.SetupLipSyncIds;

      // 回调
      setupLipSyncIds();
    };

    // LipSyncIds
    const setupLipSyncIds = (): void => {
      const lipSyncIdCount = this._modelSetting.getLipSyncParameterCount();

      for (let i = 0; i < lipSyncIdCount; ++i) {
        this._lipSyncIds.pushBack(this._modelSetting.getLipSyncParameterId(i));
      }
      this._state = LoadStep.SetupLayout;

      // 回调
      setupLayout();
    };

    // 布局
    const setupLayout = (): void => {
      const layout: csmMap<string, number> = new csmMap<string, number>();

      if (this._modelSetting == null || this._modelMatrix == null) {
        CubismLogError("setupLayout() 失败。");
        return;
      }

      this._modelSetting.getLayoutMap(layout);
      this._modelMatrix.setupFromLayout(layout);
      this._state = LoadStep.LoadMotion;

      // 回调
      loadCubismMotion();
    };

    // 运动
    const loadCubismMotion = (): void => {
      this._state = LoadStep.WaitLoadMotion;
      this._model.saveParameters();
      this._allMotionCount = 0;
      this._motionCount = 0;
      const group: string[] = [];

      const motionGroupCount: number = this._modelSetting.getMotionGroupCount();

      // 计算运动的总数
      for (let i = 0; i < motionGroupCount; i++) {
        group[i] = this._modelSetting.getMotionGroupName(i);
        this._allMotionCount += this._modelSetting.getMotionCount(group[i]);
      }

      // 载入运动
      for (let i = 0; i < motionGroupCount; i++) {
        this.preLoadMotionGroup(group[i]);
      }

      // 如果没有运动
      if (motionGroupCount == 0) {
        this._state = LoadStep.LoadTexture;

        // 停止所有运动
        this._motionManager.stopAllMotions();

        this._updating = false;
        this._initialized = true;

        this.createRenderer();
        this.setupTextures();
        this.getRenderer().startUp(gl);
      }
    };
  }

  /**
   * 将纹理加载到纹理单元中
   */
  private setupTextures(): void {
    // 在iPhone上采用premultipliedAlpha以提高透明度质量
    const usePremultiply = true;

    if (this._state == LoadStep.LoadTexture) {
      // 用于加载纹理
      const textureCount: number = this._modelSetting.getTextureCount();

      for (
        let modelTextureNumber = 0;
        modelTextureNumber < textureCount;
        modelTextureNumber++
      ) {
        // 如果纹理名称为空字符串，则跳过加载和绑定处理
        if (this._modelSetting.getTextureFileName(modelTextureNumber) == "") {
          console.log("getTextureFileName null");
          continue;
        }

        // 将纹理加载到WebGL纹理单元中
        let texturePath = this._modelSetting.getTextureFileName(
          modelTextureNumber,
        );
        texturePath = this._modelHomeDir + texturePath;

        // 纹理加载完成时调用的回调函数
        const onLoad = (textureInfo: TextureInfo): void => {
          this.getRenderer().bindTexture(modelTextureNumber, textureInfo.id);

          this._textureCount++;

          if (this._textureCount >= textureCount) {
            // 加载完成
            this._state = LoadStep.CompleteSetup;
          }
        };

        // 读取纹理
        LAppDelegate.getInstance()
          .getTextureManager()
          .createTextureFromPngFile(texturePath, usePremultiply, onLoad);
        this.getRenderer().setIsPremultipliedAlpha(usePremultiply);
      }

      this._state = LoadStep.WaitLoadTexture;
    }
  }

  /**
   * 重新构建渲染器
   */
  public reloadRenderer(): void {
    this.deleteRenderer();
    this.createRenderer();
    this.setupTextures();
  }

  /**
   * 更新
   */
  public update(): void {
    if (this._state != LoadStep.CompleteSetup) return;

    const deltaTimeSeconds: number = LAppPal.getDeltaTime();
    this._userTimeSeconds += deltaTimeSeconds;

    this._dragManager.update(deltaTimeSeconds);
    this._dragX = this._dragManager.getX();
    this._dragY = this._dragManager.getY();

    // 由运动引起的参数更新
    let motionUpdated = false;

    //--------------------------------------------------------------------------
    this._model.loadParameters(); // 加载上次保存的状态
    if (this._motionManager.isFinished()) {
      // 如果没有运动在播放，则随机播放空闲运动
      this.startRandomMotion(
        LAppDefine.MotionGroupIdle,
        LAppDefine.PriorityIdle,
      );
    } else {
      motionUpdated = this._motionManager.updateMotion(
        this._model,
        deltaTimeSeconds,
      ); // 更新运动
    }
    this._model.saveParameters(); // 保存状态
    //--------------------------------------------------------------------------

    // 眨眼
    if (!motionUpdated) {
      if (this._eyeBlink != null) {
        // 当没有主要运动更新时
        this._eyeBlink.updateParameters(this._model, deltaTimeSeconds); // 眼睛眨动
      }
    }

    if (this._expressionManager != null) {
      this._expressionManager.updateMotion(this._model, deltaTimeSeconds); // 通过表情更新参数（相对变化）
    }

    // 拖动变化
    // 通过拖动调整面部方向
    this._model.addParameterValueById(this._idParamAngleX, this._dragX * 30); // 加-30到30的值
    this._model.addParameterValueById(this._idParamAngleY, this._dragY * 30);
    this._model.addParameterValueById(
      this._idParamAngleZ,
      this._dragX * this._dragY * -30,
    );

    // 通过拖动调整身体方向
    this._model.addParameterValueById(
      this._idParamBodyAngleX,
      this._dragX * 10,
    ); // 加-10到10的值

    // 通过拖动调整眼睛方向
    this._model.addParameterValueById(this._idParamEyeBallX, this._dragX); // 加-1到1的值
    this._model.addParameterValueById(this._idParamEyeBallY, this._dragY);

    // 呼吸等
    if (this._breath != null) {
      this._breath.updateParameters(this._model, deltaTimeSeconds);
    }

    // 物理设置
    if (this._physics != null) {
      this._physics.evaluate(this._model, deltaTimeSeconds);
    }

    // 同步设置
    if (this._lipsync) {
      let value = 0.0; // 实时同步时，从系统获取音量，并在0~1范围内输入值。

      this._wavFileHandler.update(deltaTimeSeconds);
      value = this._wavFileHandler.getRms();

      for (let i = 0; i < this._lipSyncIds.getSize(); ++i) {
        this._model.addParameterValueById(this._lipSyncIds.at(i), value, 0.8);
      }
    }

    // 姿势设置
    if (this._pose != null) {
      this._pose.updateParameters(this._model, deltaTimeSeconds);
    }

    this._model.update();
  }

  /**
   * 开始播放指定组的运动
   * @param group 运动组名
   * @param no 组内编号
   * @param priority 优先级
   * @param onFinishedMotionHandler 运动播放结束时调用的回调函数
   * @return 开始的运动的标识号。用于判断单个运动是否结束的isFinished()的参数。如果不能开始，则返回[-1]
   */
  public startMotion(
    group: string,
    no: number,
    priority: number,
    onFinishedMotionHandler?: FinishedMotionCallback,
  ): CubismMotionQueueEntryHandle {
    if (priority == LAppDefine.PriorityForce) {
      this._motionManager.setReservePriority(priority);
    } else if (!this._motionManager.reserveMotion(priority)) {
      if (this._debugMode) {
        LAppPal.printMessage("[APP]无法开始运动。");
      }
      return InvalidMotionQueueEntryHandleValue;
    }

    const motionFileName = this._modelSetting.getMotionFileName(group, no);

    // 例如 idle_0
    const name = `${group}_${no}`;
    let motion: CubismMotion = this._motions.getValue(name) as CubismMotion;
    let autoDelete = false;

    if (motion == null) {
      fetch(`${this._modelHomeDir}${motionFileName}`)
        .then((response) => {
          if (response.ok) {
            return response.arrayBuffer();
          } else if (response.status >= 400) {
            CubismLogError(
              `无法加载文件 ${this._modelHomeDir}${motionFileName}`,
            );
            return new ArrayBuffer(0);
          }
        })
        .then((arrayBuffer) => {
          motion = this.loadMotion(
            arrayBuffer,
            arrayBuffer.byteLength,
            null,
            onFinishedMotionHandler,
          );

          if (motion == null) {
            return;
          }

          let fadeTime: number = this._modelSetting.getMotionFadeInTimeValue(
            group,
            no,
          );

          if (fadeTime >= 0.0) {
            motion.setFadeInTime(fadeTime);
          }

          fadeTime = this._modelSetting.getMotionFadeOutTimeValue(group, no);
          if (fadeTime >= 0.0) {
            motion.setFadeOutTime(fadeTime);
          }

          motion.setEffectIds(this._eyeBlinkIds, this._lipSyncIds);
          autoDelete = true; // 在结束时从内存中删除
        });
    } else {
      motion.setFinishedMotionHandler(onFinishedMotionHandler);
    }

    // 声音
    const voice = this._modelSetting.getMotionSoundFileName(group, no);
    if (voice.localeCompare("") != 0) {
      let path = voice;
      path = this._modelHomeDir + path;
      this._wavFileHandler.start(path);
    }

    if (this._debugMode) {
      LAppPal.printMessage(`[APP]开始运动: [${group}_${no}`);
    }
    return this._motionManager.startMotionPriority(
      motion,
      autoDelete,
      priority,
    );
  }

  /**
   * 开始播放随机选定的运动
   * @param group 运动组名
   * @param priority 优先级
   * @param onFinishedMotionHandler 运动播放结束时调用的回调函数
   * @return 开始的运动的标识号。用于判断单个运动是否结束的isFinished()的参数。如果不能开始，则返回[-1]
   */
  public startRandomMotion(
    group: string,
    priority: number,
    onFinishedMotionHandler?: FinishedMotionCallback,
  ): CubismMotionQueueEntryHandle {
    if (this._modelSetting.getMotionCount(group) == 0) {
      return InvalidMotionQueueEntryHandleValue;
    }

    const no: number = Math.floor(
      Math.random() * this._modelSetting.getMotionCount(group),
    );

    return this.startMotion(group, no, priority, onFinishedMotionHandler);
  }

  /**
   * 设置指定的表情运动
   *
   * @param expressionId 表情运动的ID
   */
  public setExpression(expressionId: string): void {
    const motion: ACubismMotion = this._expressions.getValue(expressionId);

    if (this._debugMode) {
      LAppPal.printMessage(`[APP]表情: [${expressionId}]`);
    }

    if (motion != null) {
      this._expressionManager.startMotionPriority(
        motion,
        false,
        LAppDefine.PriorityForce,
      );
    } else {
      if (this._debugMode) {
        LAppPal.printMessage(`[APP]表情[${expressionId}]为空`);
      }
    }
  }

  /**
   * 设置随机选定的表情运动
   */
  public setRandomExpression(): void {
    if (this._expressions.getSize() == 0) {
      return;
    }

    const no: number = Math.floor(Math.random() * this._expressions.getSize());

    for (let i = 0; i < this._expressions.getSize(); i++) {
      if (i == no) {
        const name: string = this._expressions._keyValues[i].first;
        this.setExpression(name);
        return;
      }
    }
  }

  /**
   * 触发事件
   */
  public motionEventFired(eventValue: csmString): void {
    CubismLogInfo("{0} 在 LAppModel 上被触发!!", eventValue.s);
  }

  /**
   * 碰撞检测
   * 从指定ID的顶点列表计算矩形，并判断坐标是否在矩形范围内。
   *
   * @param hitArenaName 碰撞检测目标的ID
   * @param x 判定的X坐标
   * @param y 判定的Y坐标
   */
  public hitTest(hitArenaName: string, x: number, y: number): boolean {
    // 透明时无碰撞检测。
    if (this._opacity < 1) {
      return false;
    }

    const count: number = this._modelSetting.getHitAreasCount();

    for (let i = 0; i < count; i++) {
      if (this._modelSetting.getHitAreaName(i) == hitArenaName) {
        const drawId: CubismIdHandle = this._modelSetting.getHitAreaId(i);
        return this.isHit(drawId, x, y);
      }
    }

    return false;
  }

  /**
   * 从组名加载所有运动数据。
   * 运动数据的名称从ModelSetting中获取。
   *
   * @param group 运动数据组名
   */
  public preLoadMotionGroup(group: string): void {
    for (let i = 0; i < this._modelSetting.getMotionCount(group); i++) {
      const motionFileName = this._modelSetting.getMotionFileName(group, i);

      // 例如 idle_0
      const name = `${group}_${i}`;
      if (this._debugMode) {
        LAppPal.printMessage(
          `[APP]加载运动: ${motionFileName} => [${name}]`,
        );
      }

      fetch(`${this._modelHomeDir}${motionFileName}`)
        .then((response) => {
          if (response.ok) {
            return response.arrayBuffer();
          } else if (response.status >= 400) {
            CubismLogError(
              `无法加载文件 ${this._modelHomeDir}${motionFileName}`,
            );
            return new ArrayBuffer(0);
          }
        })
        .then((arrayBuffer) => {
          const tmpMotion: CubismMotion = this.loadMotion(
            arrayBuffer,
            arrayBuffer.byteLength,
            name,
          );

          if (tmpMotion != null) {
            let fadeTime = this._modelSetting.getMotionFadeInTimeValue(
              group,
              i,
            );
            if (fadeTime >= 0.0) {
              tmpMotion.setFadeInTime(fadeTime);
            }

            fadeTime = this._modelSetting.getMotionFadeOutTimeValue(group, i);
            if (fadeTime >= 0.0) {
              tmpMotion.setFadeOutTime(fadeTime);
            }
            tmpMotion.setEffectIds(this._eyeBlinkIds, this._lipSyncIds);

            if (this._motions.getValue(name) != null) {
              ACubismMotion.delete(this._motions.getValue(name));
            }

            this._motions.setValue(name, tmpMotion);

            this._motionCount++;
            if (this._motionCount >= this._allMotionCount) {
              this._state = LoadStep.LoadTexture;

              // 停止所有运动
              this._motionManager.stopAllMotions();

              this._updating = false;
              this._initialized = true;

              this.createRenderer();
              this.setupTextures();
              this.getRenderer().startUp(gl);
            }
          } else {
            // 如果不能加载运动，则运动总数减少一个
            this._allMotionCount--;
          }
        });
    }
  }

  /**
   * 释放所有运动数据。
   */
  public releaseMotions(): void {
    this._motions.clear();
  }

  /**
   * 释放所有表情数据。
   */
  public releaseExpressions(): void {
    this._expressions.clear();
  }

  /**
   * 渲染模型。传递用于绘制模型的View-Projection矩阵。
   */
  public doDraw(): void {
    if (this._model == null) return;

    // 传递画布大小
    const viewport: number[] = [0, 0, canvas.width, canvas.height];

    this.getRenderer().setRenderState(frameBuffer, viewport);
    this.getRenderer().drawModel();
  }

  /**
   * 渲染模型。传递用于绘制模型的View-Projection矩阵。
   */
  public draw(matrix: CubismMatrix44): void {
    if (this._model == null) {
      return;
    }

    // 完成每个加载步骤后
    if (this._state == LoadStep.CompleteSetup) {
      matrix.multiplyByMatrix(this._modelMatrix);

      this.getRenderer().setMvpMatrix(matrix);

      this.doDraw();
    }
  }

  public async hasMocConsistencyFromFile() {
    CSM_ASSERT(this._modelSetting.getModelFileName().localeCompare(``));

    // CubismModel
    if (this._modelSetting.getModelFileName() != "") {
      const modelFileName = this._modelSetting.getModelFileName();

      const response = await fetch(`${this._modelHomeDir}${modelFileName}`);
      const arrayBuffer = await response.arrayBuffer();

      this._consistency = CubismMoc.hasMocConsistency(arrayBuffer);

      if (!this._consistency) {
        CubismLogInfo("MOC3 不一致。");
      } else {
        CubismLogInfo("MOC3 一致。");
      }

      return this._consistency;
    } else {
      LAppPal.printMessage("模型数据不存在。");
    }
  }

  /**
   * 构造函数
   */
  public constructor() {
    super();

    this._modelSetting = null;
    this._modelHomeDir = null;
    this._userTimeSeconds = 0.0;

    this._eyeBlinkIds = new csmVector<CubismIdHandle>();
    this._lipSyncIds = new csmVector<CubismIdHandle>();

    this._motions = new csmMap<string, ACubismMotion>();
    this._expressions = new csmMap<string, ACubismMotion>();

    this._hitArea = new csmVector<csmRect>();
    this._userArea = new csmVector<csmRect>();

    this._idParamAngleX = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamAngleX,
    );
    this._idParamAngleY = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamAngleY,
    );
    this._idParamAngleZ = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamAngleZ,
    );
    this._idParamEyeBallX = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamEyeBallX,
    );
    this._idParamEyeBallY = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamEyeBallY,
    );
    this._idParamBodyAngleX = CubismFramework.getIdManager().getId(
      CubismDefaultParameterId.ParamBodyAngleX,
    );

    if (LAppDefine.MOCConsistencyValidationEnable) {
      this._mocConsistency = true;
    }

    this._state = LoadStep.LoadAssets;
    this._expressionCount = 0;
    this._textureCount = 0;
    this._motionCount = 0;
    this._allMotionCount = 0;
    this._wavFileHandler = new LAppWavFileHandler();
    this._consistency = false;
  }

  _modelSetting: ICubismModelSetting; // 模型设置信息
  _modelHomeDir: string; // 模型设置所在目录
  _userTimeSeconds: number; // 累积的增量时间[秒]

  _eyeBlinkIds: csmVector<CubismIdHandle>; // 用于眨眼功能的模型参数ID
  _lipSyncIds: csmVector<CubismIdHandle>; // 用于同步功能的模型参数ID

  _motions: csmMap<string, ACubismMotion>; // 加载的运动列表
  _expressions: csmMap<string, ACubismMotion>; // 加载的表情列表

  _hitArea: csmVector<csmRect>;
  _userArea: csmVector<csmRect>;

  _idParamAngleX: CubismIdHandle; // 参数ID: ParamAngleX
  _idParamAngleY: CubismIdHandle; // 参数ID: ParamAngleY
  _idParamAngleZ: CubismIdHandle; // 参数ID: ParamAngleZ
  _idParamEyeBallX: CubismIdHandle; // 参数ID: ParamEyeBallX
  _idParamEyeBallY: CubismIdHandle; // 参数ID: ParamEyeBallY
  _idParamBodyAngleX: CubismIdHandle; // 参数ID: ParamBodyAngleX

  _state: LoadStep; // 当前状态管理
  _expressionCount: number; // 表情数据计数
  _textureCount: number; // 纹理计数
  _motionCount: number; // 运动数据计数
  _allMotionCount: number; // 总运动数量
  _wavFileHandler: LAppWavFileHandler; // wav文件处理器
  _consistency: boolean; // MOC3一致性检查管理

}
