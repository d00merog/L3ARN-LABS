/**
 * Transformer.js Service for Local AI Inference
 * Provides client-side AI capabilities using Transformer.js and ONNX models
 */

import { pipeline, Pipeline, PipelineType, env } from '@xenova/transformers';

interface ModelConfig {
  name: string;
  task: PipelineType;
  model: string;
  quantized?: boolean;
  revision?: string;
  device?: 'cpu' | 'gpu' | 'webgpu';
}

interface InferenceOptions {
  maxLength?: number;
  temperature?: number;
  topK?: number;
  topP?: number;
  doSample?: boolean;
  numReturnSequences?: number;
}

interface ModelPerformance {
  loadTime: number;
  inferenceTime: number;
  memoryUsage: number;
  tokensPerSecond: number;
}

interface LocalAICapabilities {
  webgpu: boolean;
  webgl: boolean;
  wasm: boolean;
  supportedTasks: PipelineType[];
  modelCache: boolean;
  offlineCapable: boolean;
}

class TransformerService {
  private static instance: TransformerService;
  private models: Map<string, Pipeline> = new Map();
  private modelConfigs: Map<string, ModelConfig> = new Map();
  private performance: Map<string, ModelPerformance> = new Map();
  private initialized = false;
  private capabilities: LocalAICapabilities | null = null;

  private constructor() {
    // Configure Transformers.js environment
    env.allowRemoteModels = true;
    env.allowLocalModels = true;
    env.useBrowserCache = true;
    env.useFS = false;
  }

  static getInstance(): TransformerService {
    if (!TransformerService.instance) {
      TransformerService.instance = new TransformerService();
    }
    return TransformerService.instance;
  }

  /**
   * Initialize the Transformer service and check capabilities
   */
  async initialize(): Promise<LocalAICapabilities> {
    if (this.initialized && this.capabilities) {
      return this.capabilities;
    }

    try {
      console.log('🤖 Initializing Transformer.js for local AI...');

      // Check browser capabilities
      const webgpuSupported = 'gpu' in navigator;
      const webglSupported = !!document.createElement('canvas').getContext('webgl2');
      const wasmSupported = (() => {
        try {
          if (typeof WebAssembly === 'object' && typeof WebAssembly.instantiate === 'function') {
            const module = new WebAssembly.Module(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
            return WebAssembly.validate(module);
          }
          return false;
        } catch (e) {
          return false;
        }
      })();

      // Set optimal backend based on capabilities
      if (webgpuSupported) {
        env.backends.onnx.wasm.proxy = false;
        console.log('🚀 WebGPU backend available for acceleration');
      } else if (webglSupported) {
        env.backends.onnx.webgl = { contextOptions: { antialias: false } };
        console.log('🎮 WebGL backend available for acceleration');
      }

      // Configure model caching
      env.cacheDir = './.cache/transformers';

      this.capabilities = {
        webgpu: webgpuSupported,
        webgl: webglSupported,
        wasm: wasmSupported,
        supportedTasks: [
          'text-classification',
          'token-classification', 
          'question-answering',
          'fill-mask',
          'summarization',
          'translation',
          'text2text-generation',
          'text-generation',
          'zero-shot-classification',
          'embeddings',
          'feature-extraction'
        ],
        modelCache: true,
        offlineCapable: true
      };

      // Register default educational models
      await this.registerDefaultModels();

      this.initialized = true;
      console.log('✅ Transformer.js initialized successfully');
      
      return this.capabilities;

    } catch (error) {
      console.error('❌ Transformer.js initialization failed:', error);
      this.capabilities = {
        webgpu: false,
        webgl: false,
        wasm: false,
        supportedTasks: [],
        modelCache: false,
        offlineCapable: false
      };
      return this.capabilities;
    }
  }

  /**
   * Register default educational AI models
   */
  private async registerDefaultModels(): Promise<void> {
    const defaultModels: ModelConfig[] = [
      {
        name: 'educational-qa',
        task: 'question-answering',
        model: 'Xenova/distilbert-base-cased-distilled-squad',
        quantized: true,
        device: 'cpu'
      },
      {
        name: 'code-classifier',
        task: 'text-classification',
        model: 'Xenova/distilbert-base-uncased-finetuned-sst-2-english',
        quantized: true,
        device: 'cpu'
      },
      {
        name: 'text-embeddings',
        task: 'feature-extraction',
        model: 'Xenova/all-MiniLM-L6-v2',
        quantized: true,
        device: 'cpu'
      },
      {
        name: 'code-generator',
        task: 'text-generation',
        model: 'Xenova/codegen-350M-mono',
        quantized: true,
        device: 'cpu'
      },
      {
        name: 'math-solver',
        task: 'text2text-generation',
        model: 'Xenova/flan-t5-small',
        quantized: true,
        device: 'cpu'
      },
      {
        name: 'content-summarizer',
        task: 'summarization',
        model: 'Xenova/distilbart-cnn-6-6',
        quantized: true,
        device: 'cpu'
      }
    ];

    for (const config of defaultModels) {
      this.modelConfigs.set(config.name, config);
    }

    console.log(`📚 Registered ${defaultModels.length} educational AI models`);
  }

  /**
   * Load a specific AI model for inference
   */
  async loadModel(modelName: string): Promise<boolean> {
    if (this.models.has(modelName)) {
      return true; // Already loaded
    }

    const config = this.modelConfigs.get(modelName);
    if (!config) {
      throw new Error(`Model configuration not found: ${modelName}`);
    }

    const startTime = performance.now();

    try {
      console.log(`🔄 Loading model: ${config.name} (${config.model})`);

      const model = await pipeline(config.task, config.model, {
        quantized: config.quantized,
        revision: config.revision,
        device: config.device || 'cpu',
        dtype: config.quantized ? 'q8' : 'fp32'
      });

      const loadTime = performance.now() - startTime;

      this.models.set(modelName, model);
      this.performance.set(modelName, {
        loadTime,
        inferenceTime: 0,
        memoryUsage: 0,
        tokensPerSecond: 0
      });

      console.log(`✅ Model loaded: ${config.name} in ${loadTime.toFixed(1)}ms`);
      return true;

    } catch (error) {
      console.error(`❌ Failed to load model ${modelName}:`, error);
      return false;
    }
  }

  /**
   * Educational Question Answering
   */
  async answerQuestion(
    context: string, 
    question: string, 
    options?: InferenceOptions
  ): Promise<{ answer: string; confidence: number; context: string }> {
    const modelName = 'educational-qa';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Educational QA model not available');
    }

    const startTime = performance.now();

    try {
      const result = await model({
        question,
        context
      });

      const inferenceTime = performance.now() - startTime;
      this.updatePerformanceMetrics(modelName, inferenceTime);

      return {
        answer: result.answer,
        confidence: result.score || 0,
        context: context.slice(result.start, result.end) || result.answer
      };

    } catch (error) {
      console.error('❌ Question answering failed:', error);
      throw error;
    }
  }

  /**
   * Code Quality Classification
   */
  async classifyCode(
    code: string, 
    language: string
  ): Promise<{ quality: string; confidence: number; suggestions: string[] }> {
    const modelName = 'code-classifier';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Code classifier model not available');
    }

    const startTime = performance.now();

    try {
      // Preprocess code for classification
      const preprocessedCode = `${language}: ${code.slice(0, 512)}`;
      
      const result = await model(preprocessedCode);
      const inferenceTime = performance.now() - startTime;
      
      this.updatePerformanceMetrics(modelName, inferenceTime);

      // Map classification result to quality assessment
      const qualityMap = {
        'POSITIVE': 'good',
        'NEGATIVE': 'needs_improvement'
      };

      const quality = qualityMap[result[0].label as keyof typeof qualityMap] || 'unknown';
      const confidence = result[0].score || 0;

      // Generate suggestions based on quality
      const suggestions = this.generateCodeSuggestions(code, language, quality);

      return {
        quality,
        confidence,
        suggestions
      };

    } catch (error) {
      console.error('❌ Code classification failed:', error);
      throw error;
    }
  }

  /**
   * Generate Text Embeddings for Semantic Search
   */
  async generateEmbeddings(texts: string[]): Promise<Float32Array[]> {
    const modelName = 'text-embeddings';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Text embeddings model not available');
    }

    const startTime = performance.now();

    try {
      const embeddings: Float32Array[] = [];

      for (const text of texts) {
        const result = await model(text, { pooling: 'mean', normalize: true });
        embeddings.push(new Float32Array(result.data));
      }

      const inferenceTime = performance.now() - startTime;
      this.updatePerformanceMetrics(modelName, inferenceTime);

      return embeddings;

    } catch (error) {
      console.error('❌ Embedding generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate Code Completions
   */
  async generateCode(
    prompt: string, 
    language: string, 
    options: InferenceOptions = {}
  ): Promise<{ code: string; confidence: number }> {
    const modelName = 'code-generator';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Code generator model not available');
    }

    const startTime = performance.now();

    try {
      const fullPrompt = `// Language: ${language}\n${prompt}`;
      
      const result = await model(fullPrompt, {
        max_length: options.maxLength || 100,
        temperature: options.temperature || 0.7,
        do_sample: options.doSample || true,
        top_k: options.topK || 50,
        top_p: options.topP || 0.95,
        pad_token_id: 50256
      });

      const inferenceTime = performance.now() - startTime;
      this.updatePerformanceMetrics(modelName, inferenceTime);

      // Extract generated code (remove prompt)
      const generatedText = Array.isArray(result) ? result[0].generated_text : result.generated_text;
      const code = generatedText.replace(fullPrompt, '').trim();

      return {
        code,
        confidence: 0.8 // Placeholder confidence
      };

    } catch (error) {
      console.error('❌ Code generation failed:', error);
      throw error;
    }
  }

  /**
   * Solve Math Problems
   */
  async solveMathProblem(
    problem: string, 
    context?: string
  ): Promise<{ solution: string; steps: string[]; confidence: number }> {
    const modelName = 'math-solver';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Math solver model not available');
    }

    const startTime = performance.now();

    try {
      const prompt = context 
        ? `Context: ${context}\nProblem: ${problem}\nSolution:`
        : `Solve step by step: ${problem}`;

      const result = await model(prompt, {
        max_length: 200,
        temperature: 0.3,
        do_sample: false
      });

      const inferenceTime = performance.now() - startTime;
      this.updatePerformanceMetrics(modelName, inferenceTime);

      const solutionText = Array.isArray(result) ? result[0].generated_text : result.generated_text;
      
      // Parse solution into steps
      const steps = solutionText.split('\n').filter(line => line.trim().length > 0);
      
      return {
        solution: steps[steps.length - 1] || solutionText,
        steps,
        confidence: 0.85 // Placeholder confidence
      };

    } catch (error) {
      console.error('❌ Math problem solving failed:', error);
      throw error;
    }
  }

  /**
   * Summarize Educational Content
   */
  async summarizeContent(
    text: string, 
    maxLength: number = 100
  ): Promise<{ summary: string; keyPoints: string[] }> {
    const modelName = 'content-summarizer';
    await this.loadModel(modelName);
    
    const model = this.models.get(modelName);
    if (!model) {
      throw new Error('Content summarizer model not available');
    }

    const startTime = performance.now();

    try {
      const result = await model(text, {
        max_length: maxLength,
        min_length: Math.floor(maxLength * 0.3),
        do_sample: false
      });

      const inferenceTime = performance.now() - startTime;
      this.updatePerformanceMetrics(modelName, inferenceTime);

      const summary = Array.isArray(result) ? result[0].summary_text : result.summary_text;
      
      // Extract key points (simplified)
      const keyPoints = summary.split('.').filter(point => point.trim().length > 10);

      return {
        summary,
        keyPoints
      };

    } catch (error) {
      console.error('❌ Content summarization failed:', error);
      throw error;
    }
  }

  /**
   * Generate code improvement suggestions
   */
  private generateCodeSuggestions(code: string, language: string, quality: string): string[] {
    const suggestions: string[] = [];

    if (quality === 'needs_improvement') {
      // Basic heuristic-based suggestions
      if (code.includes('console.log') && language === 'javascript') {
        suggestions.push('Consider removing debug console.log statements');
      }
      
      if (code.length < 50) {
        suggestions.push('Consider adding more comprehensive error handling');
      }
      
      if (!/function|class|def|fn/.test(code)) {
        suggestions.push('Consider organizing code into functions or classes');
      }
      
      if (!/\/\/|#|\/\*/.test(code)) {
        suggestions.push('Add comments to explain complex logic');
      }
    }

    return suggestions;
  }

  /**
   * Update performance metrics for a model
   */
  private updatePerformanceMetrics(modelName: string, inferenceTime: number): void {
    const current = this.performance.get(modelName);
    if (current) {
      current.inferenceTime = inferenceTime;
      current.tokensPerSecond = 1000 / inferenceTime; // Simplified calculation
    }
  }

  /**
   * Get model performance statistics
   */
  getPerformanceStats(): Record<string, ModelPerformance> {
    return Object.fromEntries(this.performance.entries());
  }

  /**
   * Get loaded models info
   */
  getLoadedModels(): Array<{ name: string; config: ModelConfig; loaded: boolean }> {
    return Array.from(this.modelConfigs.entries()).map(([name, config]) => ({
      name,
      config,
      loaded: this.models.has(name)
    }));
  }

  /**
   * Unload a specific model to free memory
   */
  async unloadModel(modelName: string): Promise<boolean> {
    try {
      if (this.models.has(modelName)) {
        const model = this.models.get(modelName);
        // Dispose model if it has a dispose method
        if (model && typeof model.dispose === 'function') {
          await model.dispose();
        }
        this.models.delete(modelName);
        console.log(`🗑️ Model unloaded: ${modelName}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error(`❌ Failed to unload model ${modelName}:`, error);
      return false;
    }
  }

  /**
   * Clean up all resources
   */
  async dispose(): Promise<void> {
    console.log('🧹 Disposing Transformer.js resources...');
    
    for (const modelName of this.models.keys()) {
      await this.unloadModel(modelName);
    }
    
    this.models.clear();
    this.performance.clear();
    this.initialized = false;
    
    console.log('✅ Transformer.js resources disposed');
  }

  // Getters
  get isInitialized(): boolean {
    return this.initialized;
  }

  get localCapabilities(): LocalAICapabilities | null {
    return this.capabilities;
  }

  get loadedModelCount(): number {
    return this.models.size;
  }
}

export default TransformerService;
export type { ModelConfig, InferenceOptions, ModelPerformance, LocalAICapabilities };