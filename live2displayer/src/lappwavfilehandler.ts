/**
 * 版权所有(c) Live2D Inc. 保留所有权利。
 *
 * 本源代码的使用受Live2D开放软件许可证的约束，
 * 该许可证可以在以下网址找到：https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html。
 */

/** @deprecated 由于 getInstance() 方法已弃用，该变量也已弃用。 */
export let s_instance: LAppWavFileHandler = null;

export class LAppWavFileHandler {
  /**
   * 返回类的实例（单例模式）。
   * 如果实例尚未生成，则在内部生成实例。
   *
   * @return 类的实例
   * @deprecated 该类的单例模式已弃用，请改用 new LAppWavFileHandler()。
   */
  public static getInstance(): LAppWavFileHandler {
    if (s_instance == null) {
      s_instance = new LAppWavFileHandler();
    }

    return s_instance;
  }

  /**
   * 释放类的实例（单例模式）。
   *
   * @deprecated 该方法已弃用，因为 getInstance() 已弃用。
   */
  public static releaseInstance(): void {
    if (s_instance != null) {
      s_instance = void 0;
    }

    s_instance = null;
  }

  /**
   * 更新方法，处理音频文件的更新。
   * @param deltaTimeSeconds 时间增量（秒）
   */
  public update(deltaTimeSeconds: number) {
    let goalOffset: number;
    let rms: number;

    // 数据未加载或已达到文件末尾时，不进行更新
    if (
      this._pcmData == null ||
      this._sampleOffset >= this._wavFileInfo._samplesPerChannel
    ) {
      this._lastRms = 0.0;
      return false;
    }

    // 保持经过的时间状态
    this._userTimeSeconds += deltaTimeSeconds;
    goalOffset = Math.floor(
      this._userTimeSeconds * this._wavFileInfo._samplingRate
    );
    if (goalOffset > this._wavFileInfo._samplesPerChannel) {
      goalOffset = this._wavFileInfo._samplesPerChannel;
    }

    // 计算RMS
    rms = 0.0;
    for (
      let channelCount = 0;
      channelCount < this._wavFileInfo._numberOfChannels;
      channelCount++
    ) {
      for (
        let sampleCount = this._sampleOffset;
        sampleCount < goalOffset;
        sampleCount++
      ) {
        const pcm = this._pcmData[channelCount][sampleCount];
        rms += pcm * pcm;
      }
    }
    rms = Math.sqrt(
      rms /
        (this._wavFileInfo._numberOfChannels *
          (goalOffset - this._sampleOffset))
    );

    this._lastRms = rms;
    this._sampleOffset = goalOffset;
    return true;
  }

  /**
   * 开始加载音频文件
   * @param filePath 音频文件路径
   */
  public start(filePath: string): void {
    // 初始化采样偏移位置
    this._sampleOffset = 0;
    this._userTimeSeconds = 0.0;

    // 重置RMS值
    this._lastRms = 0.0;

    this.loadWavFile(filePath);
  }

  /**
   * 获取当前RMS值
   * @return 当前RMS值
   */
  public getRms(): number {
    return this._lastRms;
  }

  /**
   * 加载WAV文件
   * @param filePath 文件路径
   * @return Promise，表示文件是否成功加载
   */
  public loadWavFile(filePath: string): Promise<boolean> {
    return new Promise(resolveValue => {
      let ret = false;

      if (this._pcmData != null) {
        this.releasePcmData();
      }

      // 异步加载文件
      const asyncFileLoad = async () => {
        return fetch(filePath).then(responce => {
          return responce.arrayBuffer();
        });
      };

      const asyncWavFileManager = (async () => {
        this._byteReader._fileByte = await asyncFileLoad();
        this._byteReader._fileDataView = new DataView(
          this._byteReader._fileByte
        );
        this._byteReader._fileSize = this._byteReader._fileByte.byteLength;
        this._byteReader._readOffset = 0;

        // 检查文件加载是否成功以及是否包含"RIFF"标识
        if (
          this._byteReader._fileByte == null ||
          this._byteReader._fileSize < 4
        ) {
          resolveValue(false);
          return;
        }

        // 设置文件名
        this._wavFileInfo._fileName = filePath;

        try {
          // 检查"RIFF"标识
          if (!this._byteReader.getCheckSignature('RIFF')) {
            ret = false;
            throw new Error('无法找到标识 "RIFF"。');
          }
          // 读取文件大小（跳过）
          this._byteReader.get32LittleEndian();
          // 检查"WAVE"标识
          if (!this._byteReader.getCheckSignature('WAVE')) {
            ret = false;
            throw new Error('无法找到标识 "WAVE"。');
          }
          // 检查"fmt "标识
          if (!this._byteReader.getCheckSignature('fmt ')) {
            ret = false;
            throw new Error('无法找到标识 "fmt"。');
          }
          // 读取fmt块大小
          const fmtChunkSize = this._byteReader.get32LittleEndian();
          // 检查格式ID是否为1（线性PCM）
          if (this._byteReader.get16LittleEndian() != 1) {
            ret = false;
            throw new Error('文件不是线性PCM格式。');
          }
          // 读取声道数
          this._wavFileInfo._numberOfChannels =
            this._byteReader.get16LittleEndian();
          // 读取采样率
          this._wavFileInfo._samplingRate =
            this._byteReader.get32LittleEndian();
          // 跳过数据速度（字节/秒）
          this._byteReader.get32LittleEndian();
          // 跳过块大小
          this._byteReader.get16LittleEndian();
          // 读取量化位数
          this._wavFileInfo._bitsPerSample =
            this._byteReader.get16LittleEndian();
          // 跳过fmt块扩展部分
          if (fmtChunkSize > 16) {
            this._byteReader._readOffset += fmtChunkSize - 16;
          }
          // 跳过直到找到"data"块
          while (
            !this._byteReader.getCheckSignature('data') &&
            this._byteReader._readOffset < this._byteReader._fileSize
          ) {
            this._byteReader._readOffset +=
              this._byteReader.get32LittleEndian() + 4;
          }
          // 未找到"data"块
          if (this._byteReader._readOffset >= this._byteReader._fileSize) {
            ret = false;
            throw new Error('无法找到 "data" 块。');
          }
          // 读取样本数
          {
            const dataChunkSize = this._byteReader.get32LittleEndian();
            this._wavFileInfo._samplesPerChannel =
              (dataChunkSize * 8) /
              (this._wavFileInfo._bitsPerSample *
                this._wavFileInfo._numberOfChannels);
          }
          // 分配内存
          this._pcmData = new Array(this._wavFileInfo._numberOfChannels);
          for (
            let channelCount = 0;
            channelCount < this._wavFileInfo._numberOfChannels;
            channelCount++
          ) {
            this._pcmData[channelCount] = new Float32Array(
              this._wavFileInfo._samplesPerChannel
            );
          }
          // 获取波形数据
          for (
            let sampleCount = 0;
            sampleCount < this._wavFileInfo._samplesPerChannel;
            sampleCount++
          ) {
            for (
              let channelCount = 0;
              channelCount < this._wavFileInfo._numberOfChannels;
              channelCount++
            ) {
              this._pcmData[channelCount][sampleCount] = this.getPcmSample();
            }
          }

          ret = true;

          resolveValue(ret);
        } catch (e) {
          console.log(e);
        }
      })().then(() => {
        resolveValue(ret);
      });
    });
  }

  /**
   * 获取PCM样本
   * @return PCM样本
   */
  public getPcmSample(): number {
    let pcm32;

    // 扩展到32位范围并转换为-1到1的范围
    switch (this._wavFileInfo._bitsPerSample) {
      case 8:
        pcm32 = this._byteReader.get8() - 128;
        pcm32 <<= 24;
        break;
      case 16:
        pcm32 = this._byteReader.get16LittleEndian() << 16;
        break;
      case 24:
        pcm32 = this._byteReader.get24LittleEndian() << 8;
        break;
      default:
        // 不支持的位宽
        pcm32 = 0;
        break;
    }

    return pcm32 / 2147483647; //Number.MAX_VALUE;
  }

  /**
   * 从指定通道获取PCM数据
   *
   * @param usechannel 使用的通道
   * @returns 指定通道的PCM数据
   */
  public getPcmDataChannel(usechannel: number): Float32Array {
    // 检查指定的通道是否有效
    if (!this._pcmData || !(usechannel < this._pcmData.length)) {
      return null;
    }

    // 从_pcmData中创建指定通道的Float32Array
    return Float32Array.from(this._pcmData[usechannel]);
  }

  /**
   * 获取音频的采样率
   *
   * @returns 音频的采样率
   */
  public getWavSamplingRate(): number {
    if (!this._wavFileInfo || this._wavFileInfo._samplingRate < 1) {
      return null;
    }

    return this._wavFileInfo._samplingRate;
  }

  /**
   * 释放PCM数据
   */
  public releasePcmData(): void {
    for (
      let channelCount = 0;
      channelCount < this._wavFileInfo._numberOfChannels;
      channelCount++
    ) {
      delete this._pcmData[channelCount];
    }
    delete this._pcmData;
    this._pcmData = null;
  }

  /**
   * 构造函数
   */
  constructor() {
    this._pcmData = null; // PCM数据
    this._userTimeSeconds = 0.0; // 用户时间（秒）
    this._lastRms = 0.0; // 最后一次RMS值
    this._sampleOffset = 0.0; // 采样偏移
    this._wavFileInfo = new WavFileInfo(); // WAV文件信息
    this._byteReader = new ByteReader(); // 字节读取器
  }

  _pcmData: Array<Float32Array>; // PCM数据
  _userTimeSeconds: number; // 用户时间（秒）
  _lastRms: number; // 最后一次RMS值
  _sampleOffset: number; // 采样偏移
  _wavFileInfo: WavFileInfo; // WAV文件信息
  _byteReader: ByteReader; // 字节读取器
  _loadFiletoBytes = (arrayBuffer: ArrayBuffer, length: number): void => {
    this._byteReader._fileByte = arrayBuffer;
    this._byteReader._fileDataView = new DataView(this._byteReader._fileByte);
    this._byteReader._fileSize = length;
  };
}

/**
 * WAV文件信息类
 */
export class WavFileInfo {
  constructor() {
    this._fileName = ''; // 文件名
    this._numberOfChannels = 0; // 通道数
    this._bitsPerSample = 0; // 每个样本的位数
    this._samplingRate = 0; // 采样率
    this._samplesPerChannel = 0; // 每个通道的样本数
  }

  _fileName: string; // 文件名
  _numberOfChannels: number; // 通道数
  _bitsPerSample: number; // 每个样本的位数
  _samplingRate: number; // 采样率
  _samplesPerChannel: number; // 每个通道的样本数
}

/**
 * 字节读取器类
 */
export class ByteReader {
  constructor() {
    this._fileByte = null; // 文件字节数据
    this._fileDataView = null; // 文件数据视图
    this._fileSize = 0; // 文件大小
    this._readOffset = 0; // 读取偏移
  }

  /**
   * 读取8位数据
   * @return 读取的8位值
   */
  public get8(): number {
    const ret = this._fileDataView.getUint8(this._readOffset);
    this._readOffset++;
    return ret;
  }

  /**
   * 读取16位数据（小端序）
   * @return 读取的16位值
   */
  public get16LittleEndian(): number {
    const ret =
      (this._fileDataView.getUint8(this._readOffset + 1) << 8) |
      this._fileDataView.getUint8(this._readOffset);
    this._readOffset += 2;
    return ret;
  }

  /**
   * 读取24位数据（小端序）
   * @return 读取的24位值（低24位）
   */
  public get24LittleEndian(): number {
    const ret =
      (this._fileDataView.getUint8(this._readOffset + 2) << 16) |
      (this._fileDataView.getUint8(this._readOffset + 1) << 8) |
      this._fileDataView.getUint8(this._readOffset);
    this._readOffset += 3;
    return ret;
  }

  /**
   * 读取32位数据（小端序）
   * @return 读取的32位值
   */
  public get32LittleEndian(): number {
    const ret =
      (this._fileDataView.getUint8(this._readOffset + 3) << 24) |
      (this._fileDataView.getUint8(this._readOffset + 2) << 16) |
      (this._fileDataView.getUint8(this._readOffset + 1) << 8) |
      this._fileDataView.getUint8(this._readOffset);
    this._readOffset += 4;
    return ret;
  }

  /**
   * 获取并检查签名与参考字符串是否匹配
   * @param reference 参考签名字符串
   * @return true表示匹配，false表示不匹配
   */
  public getCheckSignature(reference: string): boolean {
    const getSignature: Uint8Array = new Uint8Array(4);
    const referenceString: Uint8Array = new TextEncoder().encode(reference);
    if (reference.length != 4) {
      return false;
    }
    for (let signatureOffset = 0; signatureOffset < 4; signatureOffset++) {
      getSignature[signatureOffset] = this.get8();
    }
    return (
      getSignature[0] == referenceString[0] &&
      getSignature[1] == referenceString[1] &&
      getSignature[2] == referenceString[2] &&
      getSignature[3] == referenceString[3]
    );
  }

  _fileByte: ArrayBuffer; // 加载的文件字节数据
  _fileDataView: DataView; // 文件数据视图
  _fileSize: number; // 文件大小
  _readOffset: number; // 读取偏移
}
