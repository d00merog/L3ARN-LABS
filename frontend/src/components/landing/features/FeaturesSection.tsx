import React from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, Code2, Network, Coins, 
  MonitorSpeaker, Shield, Zap, Users,
  ChevronRight, Sparkles
} from 'lucide-react';

interface Feature {
  icon: React.ElementType;
  title: string;
  description: string;
  color: string;
  bgColor: string;
  features: string[];
}

const features: Feature[] = [
  {
    icon: Brain,
    title: "AI-Powered Learning",
    description: "Advanced AI tutors and personalized learning paths powered by cutting-edge machine learning.",
    color: "text-cyan-400",
    bgColor: "bg-cyan-500/10",
    features: [
      "Personalized AI tutors",
      "Adaptive learning paths", 
      "Real-time feedback",
      "Smart content recommendations"
    ]
  },
  {
    icon: Code2,
    title: "WebVM Browser Coding",
    description: "Full development environments running in your browser with WebAssembly and CheerpX technology.",
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    features: [
      "Multiple programming languages",
      "Real-time collaboration",
      "Instant code execution",
      "File system management"
    ]
  },
  {
    icon: Network,
    title: "Bittensor Network",
    description: "Decentralized AI network providing consensus-based validation and quality assurance.",
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    features: [
      "Decentralized validation",
      "Consensus algorithms",
      "Network incentives",
      "Quality assurance"
    ]
  },
  {
    icon: Coins,
    title: "TAO Token Rewards",
    description: "Earn TAO tokens for learning achievements, code contributions, and educational validation.",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    features: [
      "Learning rewards",
      "Code contributions",
      "Validation earnings",
      "Achievement bonuses"
    ]
  },
  {
    icon: MonitorSpeaker,
    title: "WebGPU Acceleration",
    description: "High-performance computing with WebGPU and Transformer.js for local AI inference.",
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    features: [
      "GPU acceleration",
      "Local AI models",
      "Fast inference",
      "Privacy-first computing"
    ]
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "End-to-end encryption, secure sandboxing, and privacy-focused architecture.",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    features: [
      "Secure sandboxing",
      "End-to-end encryption",
      "Privacy protection",
      "Data sovereignty"
    ]
  }
];

const FeaturesSection: React.FC = () => {
  return (
    <section className="py-20 bg-gray-900">
      <div className="container mx-auto px-6">
        {/* Section header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="w-6 h-6 text-yellow-400" />
            <span className="text-yellow-400 font-semibold uppercase tracking-wide">
              Revolutionary Features
            </span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Next-Generation Learning Platform
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Experience the future of education with our innovative combination of AI, 
            blockchain technology, and browser-based computing environments.
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="group relative"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
            >
              <div className="relative h-full bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:border-white/20 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/10">
                {/* Feature icon */}
                <div className={`${feature.bgColor} ${feature.color} w-16 h-16 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-8 h-8" />
                </div>

                {/* Feature content */}
                <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-purple-400 group-hover:bg-clip-text transition-all duration-300">
                  {feature.title}
                </h3>
                
                <p className="text-gray-400 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Feature list */}
                <ul className="space-y-3">
                  {feature.features.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-center gap-3 text-gray-300">
                      <ChevronRight className={`w-4 h-4 ${feature.color} flex-shrink-0`} />
                      <span className="text-sm">{item}</span>
                    </li>
                  ))}
                </ul>

                {/* Hover effect overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-600/0 to-cyan-600/0 group-hover:from-purple-600/5 group-hover:to-cyan-600/5 rounded-2xl transition-all duration-300" />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Technology showcase */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h3 className="text-2xl font-bold text-white mb-8">
            Powered by Cutting-Edge Technology
          </h3>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">BT</span>
              </div>
              <span className="text-gray-300 font-medium">Bittensor</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">WA</span>
              </div>
              <span className="text-gray-300 font-medium">WebAssembly</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">GP</span>
              </div>
              <span className="text-gray-300 font-medium">WebGPU</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="text-gray-300 font-medium">Transformer.js</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">CX</span>
              </div>
              <span className="text-gray-300 font-medium">CheerpX</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturesSection;