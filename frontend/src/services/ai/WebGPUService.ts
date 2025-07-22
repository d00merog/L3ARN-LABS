/**
 * WebGPU Service for High-Performance AI Inference
 * Provides hardware-accelerated computing capabilities in the browser
 */

interface WebGPUCapabilities {
  supported: boolean;
  adapter?: GPUAdapter;
  device?: GPUDevice;
  features: string[];
  limits: Record<string, number>;
  adapterInfo?: GPUAdapterInfo;
}

interface InferenceResult {
  output: Float32Array;
  executionTime: number;
  memoryUsed: number;
  success: boolean;
  error?: string;
}

interface ModelInfo {
  name: string;
  size: number;
  parameters: number;
  quantization: 'fp32' | 'fp16' | 'int8' | 'int4';
  framework: 'onnx' | 'tensorflow' | 'pytorch';
}

class WebGPUService {
  private static instance: WebGPUService;
  private capabilities: WebGPUCapabilities | null = null;
  private device: GPUDevice | null = null;
  private adapter: GPUAdapter | null = null;
  private initialized = false;
  private models: Map<string, any> = new Map();

  private constructor() {}

  static getInstance(): WebGPUService {
    if (!WebGPUService.instance) {
      WebGPUService.instance = new WebGPUService();
    }
    return WebGPUService.instance;
  }

  /**
   * Initialize WebGPU and check capabilities
   */
  async initialize(): Promise<WebGPUCapabilities> {
    if (this.initialized && this.capabilities) {
      return this.capabilities;
    }

    try {
      // Check WebGPU support
      if (!navigator.gpu) {
        this.capabilities = {
          supported: false,
          features: [],
          limits: {}
        };
        return this.capabilities;
      }

      console.log('🔧 Initializing WebGPU for AI inference...');

      // Request adapter
      this.adapter = await navigator.gpu.requestAdapter({
        powerPreference: 'high-performance'
      });

      if (!this.adapter) {
        throw new Error('No WebGPU adapter available');
      }

      // Get adapter info
      const adapterInfo = await this.adapter.requestAdapterInfo();

      // Request device with required features
      const requiredFeatures: GPUFeatureName[] = [];
      const availableFeatures = Array.from(this.adapter.features);
      
      // Check for useful features
      const desiredFeatures: GPUFeatureName[] = [
        'shader-f16',
        'timestamp-query',
        'texture-compression-bc',
        'texture-compression-etc2',
        'texture-compression-astc'
      ];

      for (const feature of desiredFeatures) {
        if (this.adapter.features.has(feature)) {
          requiredFeatures.push(feature);
        }
      }

      this.device = await this.adapter.requestDevice({
        requiredFeatures,
        requiredLimits: {
          maxComputeWorkgroupStorageSize: this.adapter.limits.maxComputeWorkgroupStorageSize,
          maxStorageBufferBindingSize: this.adapter.limits.maxStorageBufferBindingSize
        }
      });

      // Set up error handling
      this.device.lost.then((info) => {
        console.error('WebGPU device lost:', info.message);
        this.initialized = false;
      });

      this.capabilities = {
        supported: true,
        adapter: this.adapter,
        device: this.device,
        features: availableFeatures,
        limits: Object.fromEntries(
          Object.entries(this.adapter.limits).map(([key, value]) => [key, value])
        ),
        adapterInfo
      };

      this.initialized = true;

      console.log('✅ WebGPU initialized successfully');
      console.log('📊 Adapter:', adapterInfo);
      console.log('🚀 Features:', availableFeatures);
      
      return this.capabilities;

    } catch (error) {
      console.error('❌ WebGPU initialization failed:', error);
      this.capabilities = {
        supported: false,
        features: [],
        limits: {},
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      return this.capabilities;
    }
  }

  /**
   * Load and optimize AI model for WebGPU inference
   */
  async loadModel(modelId: string, modelUrl: string, modelInfo: ModelInfo): Promise<boolean> {
    if (!this.device) {
      throw new Error('WebGPU not initialized');
    }

    try {
      console.log(`🤖 Loading model: ${modelInfo.name}`);
      
      // Fetch model data
      const response = await fetch(modelUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch model: ${response.statusText}`);
      }

      const modelData = await response.arrayBuffer();
      console.log(`📥 Model downloaded: ${(modelData.byteLength / 1024 / 1024).toFixed(1)}MB`);

      // Create GPU buffers for model weights
      const modelBuffer = this.device.createBuffer({
        size: modelData.byteLength,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
        mappedAtCreation: true
      });

      // Copy model data to GPU
      new Uint8Array(modelBuffer.getMappedRange()).set(new Uint8Array(modelData));
      modelBuffer.unmap();

      // Store model metadata
      const model = {
        id: modelId,
        info: modelInfo,
        buffer: modelBuffer,
        loaded: true,
        loadTime: Date.now()
      };

      this.models.set(modelId, model);

      console.log(`✅ Model loaded: ${modelInfo.name} (${modelInfo.parameters.toLocaleString()} params)`);
      return true;

    } catch (error) {
      console.error(`❌ Failed to load model ${modelId}:`, error);
      return false;
    }
  }

  /**
   * Perform AI inference using WebGPU compute shaders
   */
  async runInference(
    modelId: string, 
    inputData: Float32Array, 
    outputShape: number[]
  ): Promise<InferenceResult> {
    if (!this.device) {
      throw new Error('WebGPU not initialized');
    }

    const model = this.models.get(modelId);
    if (!model) {
      throw new Error(`Model ${modelId} not loaded`);
    }

    const startTime = performance.now();

    try {
      // Create input buffer
      const inputBuffer = this.device.createBuffer({
        size: inputData.byteLength,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
        mappedAtCreation: true
      });

      new Float32Array(inputBuffer.getMappedRange()).set(inputData);
      inputBuffer.unmap();

      // Create output buffer
      const outputSize = outputShape.reduce((a, b) => a * b, 1) * 4; // 4 bytes per float32
      const outputBuffer = this.device.createBuffer({
        size: outputSize,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC
      });

      // Create staging buffer for reading results
      const stagingBuffer = this.device.createBuffer({
        size: outputSize,
        usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST
      });

      // Create compute shader for inference
      const computeShader = this.createInferenceShader(model.info);
      
      // Create compute pipeline
      const computePipeline = this.device.createComputePipeline({
        layout: 'auto',
        compute: {
          module: computeShader,
          entryPoint: 'main'
        }
      });

      // Create bind group
      const bindGroup = this.device.createBindGroup({
        layout: computePipeline.getBindGroupLayout(0),
        entries: [
          {
            binding: 0,
            resource: { buffer: model.buffer }
          },
          {
            binding: 1,
            resource: { buffer: inputBuffer }
          },
          {
            binding: 2,
            resource: { buffer: outputBuffer }
          }
        ]
      });

      // Execute computation
      const commandEncoder = this.device.createCommandEncoder();
      const passEncoder = commandEncoder.beginComputePass();
      
      passEncoder.setPipeline(computePipeline);
      passEncoder.setBindGroup(0, bindGroup);
      
      const workgroupSize = 64;
      const numWorkgroups = Math.ceil(outputShape[0] / workgroupSize);
      passEncoder.dispatchWorkgroups(numWorkgroups);
      
      passEncoder.end();

      // Copy result to staging buffer
      commandEncoder.copyBufferToBuffer(outputBuffer, 0, stagingBuffer, 0, outputSize);

      // Submit commands
      this.device.queue.submit([commandEncoder.finish()]);

      // Read results
      await stagingBuffer.mapAsync(GPUMapMode.READ);
      const outputData = new Float32Array(stagingBuffer.getMappedRange());
      const result = new Float32Array(outputData);
      stagingBuffer.unmap();

      const executionTime = performance.now() - startTime;

      // Cleanup
      inputBuffer.destroy();
      outputBuffer.destroy();
      stagingBuffer.destroy();

      return {
        output: result,
        executionTime,
        memoryUsed: inputData.byteLength + outputSize,
        success: true
      };

    } catch (error) {
      const executionTime = performance.now() - startTime;
      console.error('❌ Inference failed:', error);
      
      return {
        output: new Float32Array(0),
        executionTime,
        memoryUsed: 0,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Create compute shader for AI inference
   */
  private createInferenceShader(modelInfo: ModelInfo): GPUShaderModule {
    if (!this.device) {
      throw new Error('WebGPU not initialized');
    }

    // Basic compute shader template for neural network inference
    const shaderCode = `
      struct ModelWeights {
        data: array<f32>
      };

      struct InputData {
        data: array<f32>
      };

      struct OutputData {
        data: array<f32>
      };

      @group(0) @binding(0) var<storage, read> model: ModelWeights;
      @group(0) @binding(1) var<storage, read> input: InputData;
      @group(0) @binding(2) var<storage, read_write> output: OutputData;

      // Neural network activation functions
      fn relu(x: f32) -> f32 {
        return max(0.0, x);
      }

      fn sigmoid(x: f32) -> f32 {
        return 1.0 / (1.0 + exp(-x));
      }

      fn tanh_activation(x: f32) -> f32 {
        return tanh(x);
      }

      fn gelu(x: f32) -> f32 {
        return 0.5 * x * (1.0 + tanh(sqrt(2.0 / 3.14159) * (x + 0.044715 * x * x * x)));
      }

      // Matrix multiplication kernel
      @compute @workgroup_size(64)
      fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
        let idx = global_id.x;
        if (idx >= arrayLength(&output.data)) {
          return;
        }

        var sum: f32 = 0.0;
        
        // Simple linear transformation (can be extended for complex models)
        let input_size = arrayLength(&input.data);
        let output_size = arrayLength(&output.data);
        
        for (var i: u32 = 0u; i < input_size; i = i + 1u) {
          let weight_idx = idx * input_size + i;
          if (weight_idx < arrayLength(&model.data)) {
            sum = sum + input.data[i] * model.data[weight_idx];
          }
        }

        // Apply activation function based on model type
        ${modelInfo.framework === 'tensorflow' ? 
          'output.data[idx] = gelu(sum);' : 
          'output.data[idx] = relu(sum);'
        }
      }
    `;

    return this.device.createShaderModule({
      code: shaderCode
    });
  }

  /**
   * Get memory usage statistics
   */
  getMemoryStats(): Record<string, number> {
    if (!this.capabilities) {
      return {};
    }

    return {
      maxBufferSize: this.capabilities.limits.maxBufferSize || 0,
      maxStorageBufferBindingSize: this.capabilities.limits.maxStorageBufferBindingSize || 0,
      maxComputeWorkgroupStorageSize: this.capabilities.limits.maxComputeWorkgroupStorageSize || 0,
      modelsLoaded: this.models.size,
      totalModelMemory: Array.from(this.models.values())
        .reduce((sum, model) => sum + (model.buffer?.size || 0), 0)
    };
  }

  /**
   * Benchmark WebGPU performance
   */
  async benchmark(): Promise<{
    computePerformance: number;
    memoryBandwidth: number;
    features: string[];
  }> {
    if (!this.device) {
      throw new Error('WebGPU not initialized');
    }

    console.log('🏃‍♂️ Running WebGPU benchmark...');

    // Simple compute benchmark
    const dataSize = 1024 * 1024; // 1M floats
    const testData = new Float32Array(dataSize).map(() => Math.random());

    const startTime = performance.now();
    
    // Create a simple compute operation
    const result = await this.runInference('benchmark', testData, [dataSize]);
    
    const endTime = performance.now();
    const computeTime = endTime - startTime;

    const computePerformance = dataSize / computeTime; // Operations per millisecond
    const memoryBandwidth = (dataSize * 4 * 2) / (computeTime / 1000) / (1024 * 1024); // MB/s

    console.log(`📊 Compute Performance: ${computePerformance.toFixed(0)} ops/ms`);
    console.log(`💾 Memory Bandwidth: ${memoryBandwidth.toFixed(1)} MB/s`);

    return {
      computePerformance,
      memoryBandwidth,
      features: this.capabilities?.features || []
    };
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    // Destroy all model buffers
    for (const [modelId, model] of this.models) {
      if (model.buffer) {
        model.buffer.destroy();
      }
    }
    this.models.clear();

    if (this.device) {
      this.device.destroy();
      this.device = null;
    }

    this.adapter = null;
    this.capabilities = null;
    this.initialized = false;

    console.log('🧹 WebGPU resources cleaned up');
  }

  // Getters
  get isSupported(): boolean {
    return this.capabilities?.supported ?? false;
  }

  get isInitialized(): boolean {
    return this.initialized;
  }

  get deviceCapabilities(): WebGPUCapabilities | null {
    return this.capabilities;
  }

  get loadedModels(): string[] {
    return Array.from(this.models.keys());
  }
}

export default WebGPUService;
export type { WebGPUCapabilities, InferenceResult, ModelInfo };